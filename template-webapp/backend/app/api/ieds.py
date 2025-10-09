"""
IED Explorer API endpoints
Provides access to IEC 61850 IED hierarchy and metadata
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.scl_file import SCLFile
from app.rdf.client import RDFClient
from app.core.config import settings
import urllib.parse

router = APIRouter()


def build_ied_list_query(group_by: str, search: str = "") -> str:
    """Build SPARQL query to get IED list with grouping info"""

    search_filter = ""
    if search:
        search_filter = f'FILTER(CONTAINS(LCASE(?name), LCASE("{search}")))'

    # Base query to get IEDs
    query = f"""
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?ied ?name ?type ?manufacturer ?desc
    WHERE {{
      ?ied rdf:type iec:IED .
      OPTIONAL {{ ?ied iec:name ?name }}
      OPTIONAL {{ ?ied iec:type ?type }}
      OPTIONAL {{ ?ied iec:manufacturer ?manufacturer }}
      OPTIONAL {{ ?ied iec:desc ?desc }}
      {search_filter}
    }}
    ORDER BY ?type ?name
    LIMIT 1000
    """

    return query


def build_ied_hierarchy_query(search: str = "") -> str:
    """Build SPARQL query to get full electrical hierarchy: Substation > VoltageLevel > Bay > IEDs"""

    search_filter = ""
    if search:
        search_filter = f'FILTER(CONTAINS(LCASE(?iedName), LCASE("{search}")))'

    query = f"""
    PREFIX iec: <http://iec61850.com/SCL#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT
      ?substation ?substationName
      ?voltageLevel ?voltageLevelName ?voltage ?voltageUnit ?voltageMultiplier
      ?bay ?bayName ?bayDesc
      ?ied ?iedName ?iedType ?iedManufacturer ?iedDesc
    WHERE {{
      # Start from Substation
      ?scl rdf:type iec:SCL .
      ?scl iec:hasSubstation ?substation .
      ?substation rdf:type iec:Substation .
      OPTIONAL {{ ?substation iec:name ?substationName }}

      # Get VoltageLevel
      ?substation iec:hasVoltageLevel ?voltageLevel .
      ?voltageLevel rdf:type iec:VoltageLevel .
      OPTIONAL {{ ?voltageLevel iec:name ?voltageLevelName }}

      # Get Voltage info
      OPTIONAL {{
        ?voltageLevel iec:hasVoltage ?voltageNode .
        OPTIONAL {{ ?voltageNode iec:textContent ?voltage }}
        OPTIONAL {{ ?voltageNode iec:unit ?voltageUnit }}
        OPTIONAL {{ ?voltageNode iec:multiplier ?voltageMultiplier }}
      }}

      # Get Bay
      ?voltageLevel iec:hasBay ?bay .
      ?bay rdf:type iec:Bay .
      OPTIONAL {{ ?bay iec:name ?bayName }}
      OPTIONAL {{ ?bay iec:desc ?bayDesc }}

      # Get IEDs via LNode references
      OPTIONAL {{
        ?bay iec:hasFunction ?function .
        ?function iec:hasLNode ?lNode .
        ?lNode iec:iedName ?iedName .

        # Match with actual IED
        ?ied rdf:type iec:IED .
        ?ied iec:name ?iedName .
        OPTIONAL {{ ?ied iec:type ?iedType }}
        OPTIONAL {{ ?ied iec:manufacturer ?iedManufacturer }}
        OPTIONAL {{ ?ied iec:desc ?iedDesc }}
      }}

      {search_filter}
    }}
    ORDER BY ?substationName ?voltageLevelName ?bayName ?iedName
    LIMIT 2000
    """

    return query


def extract_binding_value(binding: Dict) -> str:
    """Extract value from SPARQL binding"""
    return binding.get("value", "") if binding else ""


def group_ieds_by_field(results: List[Dict], field: str) -> Dict[str, List[Dict]]:
    """Group IED results by a specific field"""
    grouped = {}

    for binding in results:
        key = extract_binding_value(binding.get(field))
        if not key:
            key = "Unknown"

        if key not in grouped:
            grouped[key] = []

        grouped[key].append({
            "uri": extract_binding_value(binding.get("ied")),
            "name": extract_binding_value(binding.get("name")),
            "type": extract_binding_value(binding.get("type")),
            "manufacturer": extract_binding_value(binding.get("manufacturer")),
            "description": extract_binding_value(binding.get("desc"))
        })

    return grouped


def build_hierarchy_structure(results: List[Dict]) -> Dict:
    """Build hierarchical structure from SPARQL results: Substation > VoltageLevel > Bay > IEDs"""
    hierarchy = {}

    for binding in results:
        # Extract all values
        substation_name = extract_binding_value(binding.get("substationName")) or "Unknown Substation"

        voltage_level_name = extract_binding_value(binding.get("voltageLevelName")) or "Unknown Level"
        voltage = extract_binding_value(binding.get("voltage"))
        voltage_unit = extract_binding_value(binding.get("voltageUnit"))
        voltage_multiplier = extract_binding_value(binding.get("voltageMultiplier"))

        bay_name = extract_binding_value(binding.get("bayName")) or "Unknown Bay"
        bay_desc = extract_binding_value(binding.get("bayDesc"))

        ied_name = extract_binding_value(binding.get("iedName"))

        # Build voltage level display name
        vl_display = voltage_level_name
        if voltage:
            # Check if it's the station level (0kV)
            if voltage == "0":
                vl_display += " (Station Level)"
            else:
                vl_display += f" ({voltage}"
                if voltage_multiplier:
                    vl_display += voltage_multiplier
                if voltage_unit:
                    vl_display += voltage_unit
                vl_display += ")"
        elif voltage_level_name == "0":
            # No voltage info but name is "0"
            vl_display = "0 (Station Level)"

        # Build bay display name
        bay_display = bay_name
        if bay_desc:
            bay_display += f" - {bay_desc}"

        # Initialize hierarchy levels
        if substation_name not in hierarchy:
            hierarchy[substation_name] = {}

        if vl_display not in hierarchy[substation_name]:
            hierarchy[substation_name][vl_display] = {}

        if bay_display not in hierarchy[substation_name][vl_display]:
            hierarchy[substation_name][vl_display][bay_display] = []

        # Add IED if present
        if ied_name:
            ied_data = {
                "uri": extract_binding_value(binding.get("ied")),
                "name": ied_name,
                "type": extract_binding_value(binding.get("iedType")),
                "manufacturer": extract_binding_value(binding.get("iedManufacturer")),
                "description": extract_binding_value(binding.get("iedDesc"))
            }

            # Avoid duplicates
            if not any(ied["name"] == ied_name for ied in hierarchy[substation_name][vl_display][bay_display]):
                hierarchy[substation_name][vl_display][bay_display].append(ied_data)

    return hierarchy


@router.get("/ieds")
async def get_ieds(
    file_id: int,
    group_by: str = Query("type", regex="^(type|bay)$"),
    search: str = "",
    db: Session = Depends(get_db)
):
    """
    Get list of IEDs with grouping

    Args:
        file_id: SCL file ID
        group_by: Group by 'type' or 'bay' (bay = electrical hierarchy)
        search: Optional search filter
    """
    # Get SCL file
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()
    if not scl_file:
        raise HTTPException(status_code=404, detail="SCL file not found")

    if not scl_file.fuseki_dataset:
        raise HTTPException(status_code=400, detail="File not yet uploaded to RDF store")

    # Query Fuseki
    rdf_client = RDFClient()

    try:
        if group_by == "bay":
            # Return hierarchical structure: Substation > VoltageLevel > Bay > IEDs
            query = build_ied_hierarchy_query(search)
            results = rdf_client.query(scl_file.fuseki_dataset, query)
            hierarchy = build_hierarchy_structure(results)

            # Count total IEDs
            total_ieds = 0
            for substation in hierarchy.values():
                for voltage_level in substation.values():
                    for bay_ieds in voltage_level.values():
                        total_ieds += len(bay_ieds)

            return {
                "group_by": group_by,
                "search": search,
                "hierarchy": hierarchy,
                "total_ieds": total_ieds
            }
        else:  # group by type
            query = build_ied_list_query(group_by, search)
            results = rdf_client.query(scl_file.fuseki_dataset, query)
            grouped = group_ieds_by_field(results, "type")

            return {
                "group_by": group_by,
                "search": search,
                "groups": grouped,
                "total_ieds": len(results)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying IEDs: {str(e)}")


def build_ied_children_query(parent_uri: str, parent_type: str) -> str:
    """Build SPARQL query to get children of a specific IED hierarchy element"""

    # Map parent types to their child relationship
    type_to_query = {
        "IED": f"""
            PREFIX iec: <http://iec61850.com/SCL#>
            SELECT ?child ?name ?type
            WHERE {{
              <{parent_uri}> iec:hasAccessPoint ?child .
              OPTIONAL {{ ?child iec:name ?name }}
              BIND("AccessPoint" as ?type)
            }}
        """,

        "AccessPoint": f"""
            PREFIX iec: <http://iec61850.com/SCL#>
            SELECT ?child ?name ?type
            WHERE {{
              <{parent_uri}> iec:hasServer ?child .
              BIND("Server" as ?name)
              BIND("Server" as ?type)
            }}
        """,

        "Server": f"""
            PREFIX iec: <http://iec61850.com/SCL#>
            SELECT ?child ?inst ?ldName ?type
            WHERE {{
              <{parent_uri}> iec:hasLDevice ?child .
              OPTIONAL {{ ?child iec:inst ?inst }}
              OPTIONAL {{ ?child iec:ldName ?ldName }}
              BIND("LDevice" as ?type)
            }}
        """,

        "LDevice": f"""
            PREFIX iec: <http://iec61850.com/SCL#>
            SELECT ?child ?lnClass ?lnType ?prefix ?inst ?type
            WHERE {{
              {{
                <{parent_uri}> iec:hasLN0 ?child .
                BIND("LN0" as ?type)
              }} UNION {{
                <{parent_uri}> iec:hasLN ?child .
                BIND("LN" as ?type)
              }}
              OPTIONAL {{ ?child iec:lnClass ?lnClass }}
              OPTIONAL {{ ?child iec:lnType ?lnType }}
              OPTIONAL {{ ?child iec:prefix ?prefix }}
              OPTIONAL {{ ?child iec:inst ?inst }}
            }}
            ORDER BY ?type ?lnClass ?inst
        """,

        "LN0": f"""
            PREFIX iec: <http://iec61850.com/SCL#>
            SELECT ?child ?name ?type ?category
            WHERE {{
              {{
                <{parent_uri}> iec:hasDataSet ?child .
                OPTIONAL {{ ?child iec:name ?name }}
                BIND("DataSet" as ?type)
                BIND("data" as ?category)
              }} UNION {{
                <{parent_uri}> iec:hasGSEControl ?child .
                OPTIONAL {{ ?child iec:name ?name }}
                BIND("GSEControl" as ?type)
                BIND("communication" as ?category)
              }} UNION {{
                <{parent_uri}> iec:hasSampledValueControl ?child .
                OPTIONAL {{ ?child iec:name ?name }}
                BIND("SampledValueControl" as ?type)
                BIND("communication" as ?category)
              }} UNION {{
                <{parent_uri}> iec:hasReportControl ?child .
                OPTIONAL {{ ?child iec:name ?name }}
                BIND("ReportControl" as ?type)
                BIND("communication" as ?category)
              }} UNION {{
                <{parent_uri}> iec:hasDOI ?child .
                OPTIONAL {{ ?child iec:name ?name }}
                BIND("DOI" as ?type)
                BIND("data" as ?category)
              }}
            }}
            ORDER BY ?category ?type ?name
        """,

        "LN": f"""
            PREFIX iec: <http://iec61850.com/SCL#>
            SELECT ?child ?name ?type ?category
            WHERE {{
              {{
                <{parent_uri}> iec:hasDOI ?child .
                OPTIONAL {{ ?child iec:name ?name }}
                BIND("DOI" as ?type)
                BIND("data" as ?category)
              }} UNION {{
                <{parent_uri}> iec:hasInputs ?child .
                BIND("Inputs" as ?name)
                BIND("Inputs" as ?type)
                BIND("inputs" as ?category)
              }}
            }}
            ORDER BY ?category ?type ?name
        """,

        "DataSet": f"""
            PREFIX iec: <http://iec61850.com/SCL#>
            SELECT ?child ?ldInst ?prefix ?lnClass ?lnInst ?doName ?daName ?fc ?type
            WHERE {{
              <{parent_uri}> iec:hasFCDA ?child .
              OPTIONAL {{ ?child iec:ldInst ?ldInst }}
              OPTIONAL {{ ?child iec:prefix ?prefix }}
              OPTIONAL {{ ?child iec:lnClass ?lnClass }}
              OPTIONAL {{ ?child iec:lnInst ?lnInst }}
              OPTIONAL {{ ?child iec:doName ?doName }}
              OPTIONAL {{ ?child iec:daName ?daName }}
              OPTIONAL {{ ?child iec:fc ?fc }}
              BIND("FCDA" as ?type)
            }}
        """,

        "Inputs": f"""
            PREFIX iec: <http://iec61850.com/SCL#>
            SELECT ?child ?iedName ?ldInst ?prefix ?lnClass ?lnInst ?doName ?daName ?type
            WHERE {{
              <{parent_uri}> iec:hasExtRef ?child .
              OPTIONAL {{ ?child iec:iedName ?iedName }}
              OPTIONAL {{ ?child iec:ldInst ?ldInst }}
              OPTIONAL {{ ?child iec:prefix ?prefix }}
              OPTIONAL {{ ?child iec:lnClass ?lnClass }}
              OPTIONAL {{ ?child iec:lnInst ?lnInst }}
              OPTIONAL {{ ?child iec:doName ?doName }}
              OPTIONAL {{ ?child iec:daName ?daName }}
              BIND("ExtRef" as ?type)
            }}
        """
    }

    return type_to_query.get(parent_type, "")


@router.get("/ieds/tree")
async def get_ied_tree(
    file_id: int,
    parent_uri: str,
    parent_type: str,
    db: Session = Depends(get_db)
):
    """
    Get children of a specific node in the IED tree

    Args:
        file_id: SCL file ID
        parent_uri: URI of the parent node (URL encoded)
        parent_type: Type of parent node (IED, AccessPoint, Server, LDevice, LN0, LN, etc.)
    """
    # Get SCL file
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()
    if not scl_file:
        raise HTTPException(status_code=404, detail="SCL file not found")

    if not scl_file.fuseki_dataset:
        raise HTTPException(status_code=400, detail="File not yet uploaded to RDF store")

    # Decode URI
    decoded_uri = urllib.parse.unquote(parent_uri)

    # Build query
    query = build_ied_children_query(decoded_uri, parent_type)

    if not query:
        raise HTTPException(status_code=400, detail=f"Unknown parent type: {parent_type}")

    # Query Fuseki
    rdf_client = RDFClient()

    try:
        results = rdf_client.query(scl_file.fuseki_dataset, query)

        # Format results as tree nodes
        children = []
        for binding in results:
            child_type = extract_binding_value(binding.get("type"))
            node = {
                "uri": extract_binding_value(binding.get("child")),
                "type": child_type,
                # Only these node types have children - DOI, FCDA, ExtRef are leaf nodes
                "hasChildren": child_type in ["AccessPoint", "Server", "LDevice", "LN0", "LN", "DataSet", "Inputs"]
            }

            # Build display name based on type
            if parent_type == "Server":
                # Server's children are LDevices
                inst = extract_binding_value(binding.get("inst"))
                ldName = extract_binding_value(binding.get("ldName"))
                node["name"] = f"{inst}" + (f" ({ldName})" if ldName else "")
            elif parent_type == "LDevice":
                # LDevice's children are LN0 and LN
                lnClass = extract_binding_value(binding.get("lnClass"))
                prefix = extract_binding_value(binding.get("prefix"))
                inst = extract_binding_value(binding.get("inst"))
                # Build name: prefix + lnClass + inst (e.g., "I01ATCTR11" or "LPHD0")
                name_parts = []
                if prefix:
                    name_parts.append(prefix)
                if lnClass:
                    name_parts.append(lnClass)
                if inst:
                    name_parts.append(inst)
                node["name"] = "".join(name_parts) if name_parts else "Unknown LN"
                node["lnClass"] = lnClass
            elif parent_type == "DataSet":
                # FCDA display
                parts = []
                ldInst = extract_binding_value(binding.get("ldInst"))
                if ldInst:
                    parts.append(ldInst)
                ln_parts = []
                prefix_val = extract_binding_value(binding.get("prefix"))
                lnClass_val = extract_binding_value(binding.get("lnClass"))
                lnInst_val = extract_binding_value(binding.get("lnInst"))
                if prefix_val:
                    ln_parts.append(prefix_val)
                if lnClass_val:
                    ln_parts.append(lnClass_val)
                if lnInst_val:
                    ln_parts.append(lnInst_val)
                if ln_parts:
                    parts.append("".join(ln_parts))
                doName = extract_binding_value(binding.get("doName"))
                if doName:
                    parts.append(doName)
                daName = extract_binding_value(binding.get("daName"))
                if daName:
                    parts.append(daName)
                fc = extract_binding_value(binding.get("fc"))
                node["name"] = ".".join(parts) + (f" [{fc}]" if fc else "")
            elif parent_type == "Inputs":
                # ExtRef display
                parts = []
                iedName = extract_binding_value(binding.get("iedName"))
                if iedName:
                    parts.append(iedName)
                ldInst = extract_binding_value(binding.get("ldInst"))
                if ldInst:
                    parts.append(ldInst)
                ln_parts = []
                prefix_val = extract_binding_value(binding.get("prefix"))
                lnClass_val = extract_binding_value(binding.get("lnClass"))
                lnInst_val = extract_binding_value(binding.get("lnInst"))
                if prefix_val:
                    ln_parts.append(prefix_val)
                if lnClass_val:
                    ln_parts.append(lnClass_val)
                if lnInst_val:
                    ln_parts.append(lnInst_val)
                if ln_parts:
                    parts.append("".join(ln_parts))
                doName = extract_binding_value(binding.get("doName"))
                if doName:
                    parts.append(doName)
                daName = extract_binding_value(binding.get("daName"))
                if daName:
                    parts.append(daName)
                node["name"] = "/".join(parts)
            else:
                name_val = extract_binding_value(binding.get("name"))
                inst_val = extract_binding_value(binding.get("inst"))
                node["name"] = name_val or inst_val or ""

            # Add metadata
            for key, value in binding.items():
                if key not in ["child", "type", "name"]:
                    node[key] = extract_binding_value(value)

            children.append(node)

        return {
            "parent_uri": decoded_uri,
            "parent_type": parent_type,
            "children": children,
            "count": len(children)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying tree: {str(e)}")
