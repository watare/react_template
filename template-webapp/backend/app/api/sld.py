"""
API endpoints pour la génération de schémas unifilaires (Single Line Diagrams)

Endpoints:
- POST /api/sld/generate-simple : Génère un SLD simple (POC sans PowSyBl)
- POST /api/sld/generate : Génère un SLD complet (avec PowSyBl, à venir)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging
import os
import json

from app.db.base import get_db
from app.models import User, SCLFile
from app.auth.dependencies import get_current_user
from app.rdf.client import rdf_client
from app.converters.sld_queries import (
    get_substation_topology_query,
    get_primary_equipment_query,
    get_sld_complete_query
)
from app.sld.simple_svg_generator import generate_simple_svg
from rdflib import Graph

router = APIRouter(prefix="/sld", tags=["sld"])
logger = logging.getLogger(__name__)

# Path to QElectroTech symbols
SYMBOLS_DIR = os.path.join(os.path.dirname(__file__), "..", "sld", "symbols", "svg")


class SLDGenerateRequest(BaseModel):
    """Request body for SLD generation"""
    file_id: int


def extract_binding_value(binding):
    """Extrait la valeur d'un binding SPARQL"""
    if binding is None:
        return None
    return str(binding)


@router.post("/generate-simple")
async def generate_simple_sld(
    request: SLDGenerateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère un schéma unifilaire simple (POC)

    Cette version utilise un générateur SVG basique en Python
    pour valider que les requêtes SPARQL extraient bien les bonnes données.

    Args:
        file_id: ID du fichier SCL

    Returns:
        {
            "svg": "<svg>...</svg>",
            "statistics": {
                "substations": 1,
                "voltage_levels": 3,
                "bays": 12,
                "equipments": 45
            }
        }
    """
    # Extract file_id from request body
    file_id = request.file_id

    logger.info(f"Generating simple SLD for file_id={file_id}, user={current_user.username}")

    # 1. Vérifier que le fichier existe
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()
    if not scl_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SCL file with id {file_id} not found"
        )

    # 2. Exécuter la requête SPARQL combinée (optimisée) sur Fuseki
    logger.info("Executing SPARQL query to extract SLD data")
    query = get_sld_complete_query()

    try:
        results = rdf_client.query(scl_file.fuseki_dataset, query)
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute SPARQL query: {str(e)}"
        )

    logger.info(f"SPARQL query returned {len(results)} rows")

    # 3. Organiser les résultats (bindings JSON de Fuseki)
    topology_data = {
        "substations": set(),
        "voltage_levels": [],
        "bays": [],
        "equipments": []
    }

    voltage_levels_seen = {}
    bays_seen = {}

    for binding in results:
        # Extraire les valeurs des bindings JSON
        substation_name = binding.get("substationName", {}).get("value")
        vl_name = binding.get("voltageLevelName", {}).get("value")
        bay_name = binding.get("bayName", {}).get("value")

        if not all([substation_name, vl_name, bay_name]):
            continue

        topology_data["substations"].add(substation_name)

        # VoltageLevel (dédupliqué)
        vl_key = f"{substation_name}_{vl_name}"
        if vl_key not in voltage_levels_seen:
            voltage_levels_seen[vl_key] = True
            voltage = binding.get("voltage", {}).get("value") or binding.get("nomFreq", {}).get("value")
            topology_data["voltage_levels"].append({
                "substationName": substation_name,
                "voltageLevelName": vl_name,
                "voltage": voltage
            })

        # Bay (dédupliqué)
        bay_key = f"{substation_name}_{vl_name}_{bay_name}"
        if bay_key not in bays_seen:
            bays_seen[bay_key] = True
            voltage = binding.get("voltage", {}).get("value") or binding.get("nomFreq", {}).get("value")
            topology_data["bays"].append({
                "substationName": substation_name,
                "voltageLevelName": vl_name,
                "bayName": bay_name,
                "voltage": voltage
            })

        # Equipment (peut être None si Bay vide)
        equipment_name = binding.get("equipmentName", {}).get("value")
        if equipment_name:
            # Extract order (convert to int, default to 999 if not present)
            order_value = binding.get("equipmentOrder", {}).get("value")
            try:
                equipment_order = int(order_value) if order_value else 999
            except (ValueError, TypeError):
                equipment_order = 999

            topology_data["equipments"].append({
                "substationName": substation_name,
                "voltageLevelName": vl_name,
                "bayName": bay_name,
                "equipmentName": equipment_name,
                "equipmentType": binding.get("equipmentType", {}).get("value"),
                "equipmentSubtype": binding.get("equipmentSubtype", {}).get("value"),
                "equipmentOrder": equipment_order
            })

    # 5. Statistiques
    statistics = {
        "substations": len(topology_data["substations"]),
        "voltage_levels": len(topology_data["voltage_levels"]),
        "bays": len(topology_data["bays"]),
        "equipments": len(topology_data["equipments"]),
        "triples_extracted": len(results),
        "original_file_size": scl_file.file_size if hasattr(scl_file, 'file_size') else None
    }

    logger.info(f"SLD data extracted: {statistics}")

    # 6. Générer le SVG simple
    try:
        svg = generate_simple_svg(topology_data)
    except Exception as e:
        logger.error(f"Error generating SVG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SVG: {str(e)}"
        )

    logger.info(f"SVG generated successfully, size: {len(svg)} bytes")

    return {
        "svg": svg,
        "statistics": statistics,
        "file_name": scl_file.filename,
        "generator": "simple-svg-poc"
    }


@router.post("/generate-data")
async def generate_sld_data(
    request: SLDGenerateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère les données structurées pour un SLD interactif (component-based)

    Retourne la topologie organisée pour un rendu React component-based,
    permettant l'interactivité (clic, hover, édition future).

    Args:
        file_id: ID du fichier SCL

    Returns:
        {
            "substations": [{name, voltage_levels: [...]}],
            "statistics": {...},
            "file_name": "..."
        }
    """
    file_id = request.file_id

    logger.info(f"Generating SLD data for file_id={file_id}, user={current_user.username}")

    # 1. Vérifier que le fichier existe
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()
    if not scl_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SCL file with id {file_id} not found"
        )

    # 2. Exécuter la requête SPARQL
    logger.info("Executing SPARQL query to extract SLD data")
    query = get_sld_complete_query()

    try:
        results = rdf_client.query(scl_file.fuseki_dataset, query)
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute SPARQL query: {str(e)}"
        )

    logger.info(f"SPARQL query returned {len(results)} rows")

    # 3. Organiser en structure hiérarchique pour component-based rendering
    substations_dict = {}

    for binding in results:
        substation_name = binding.get("substationName", {}).get("value")
        vl_name = binding.get("voltageLevelName", {}).get("value")
        bay_name = binding.get("bayName", {}).get("value")

        if not all([substation_name, vl_name, bay_name]):
            continue

        # Initialiser substation
        if substation_name not in substations_dict:
            substations_dict[substation_name] = {
                "name": substation_name,
                "voltage_levels": {}
            }

        # Initialiser voltage level
        if vl_name not in substations_dict[substation_name]["voltage_levels"]:
            voltage = binding.get("voltage", {}).get("value") or binding.get("nomFreq", {}).get("value")
            substations_dict[substation_name]["voltage_levels"][vl_name] = {
                "name": vl_name,
                "voltage": voltage,
                "bays": {}
            }

        # Initialiser bay
        if bay_name not in substations_dict[substation_name]["voltage_levels"][vl_name]["bays"]:
            is_coupling = ("CBO" in bay_name.upper() or "COUPL" in bay_name.upper())
            substations_dict[substation_name]["voltage_levels"][vl_name]["bays"][bay_name] = {
                "name": bay_name,
                "is_coupling": is_coupling,
                "equipments": []
            }

        # Ajouter equipment
        equipment_name = binding.get("equipmentName", {}).get("value")
        if equipment_name:
            order_value = binding.get("equipmentOrder", {}).get("value")
            try:
                equipment_order = int(order_value) if order_value else 999
            except (ValueError, TypeError):
                equipment_order = 999

            substations_dict[substation_name]["voltage_levels"][vl_name]["bays"][bay_name]["equipments"].append({
                "name": equipment_name,
                "type": binding.get("equipmentType", {}).get("value"),
                "subtype": binding.get("equipmentSubtype", {}).get("value"),
                "order": equipment_order
            })

    # 4. Convertir en liste et trier les équipements
    substations_list = []
    for substation_name, substation_data in substations_dict.items():
        voltage_levels_list = []
        for vl_name, vl_data in substation_data["voltage_levels"].items():
            bays_list = []
            for bay_name, bay_data in vl_data["bays"].items():
                # Trier les équipements par ordre
                bay_data["equipments"].sort(key=lambda eq: (eq["order"], eq["name"]))
                # Ne garder que les bays non vides
                if len(bay_data["equipments"]) > 0:
                    bays_list.append(bay_data)

            # Ne garder que les voltage levels avec des bays non vides
            if len(bays_list) > 0:
                vl_data["bays"] = bays_list
                voltage_levels_list.append(vl_data)

        substation_data["voltage_levels"] = voltage_levels_list
        substations_list.append(substation_data)

    # 5. Statistiques
    total_bays = sum(len(vl["bays"]) for sub in substations_list for vl in sub["voltage_levels"])
    total_equipments = sum(len(bay["equipments"]) for sub in substations_list for vl in sub["voltage_levels"] for bay in vl["bays"])

    statistics = {
        "substations": len(substations_list),
        "voltage_levels": sum(len(sub["voltage_levels"]) for sub in substations_list),
        "bays": total_bays,
        "equipments": total_equipments,
        "triples_extracted": len(results)
    }

    logger.info(f"SLD data organized: {statistics}")

    return {
        "substations": substations_list,
        "statistics": statistics,
        "file_name": scl_file.filename,
        "generator": "component-based"
    }


@router.get("/symbols")
async def get_symbols_library():
    """
    Retourne la bibliothèque de symboles QElectroTech disponibles

    Returns:
        {
            "CBR": {"name": "...", "file": "CBR.svg", "width": 40, "height": 130, ...},
            ...
        }
    """
    symbols_json_path = os.path.join(SYMBOLS_DIR, "symbols_library.json")

    if not os.path.exists(symbols_json_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symbols library not found"
        )

    try:
        with open(symbols_json_path, 'r') as f:
            symbols_library = json.load(f)
        return symbols_library
    except Exception as e:
        logger.error(f"Error reading symbols library: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading symbols library: {str(e)}"
        )


@router.get("/symbols/{symbol_type}")
async def get_symbol_svg(symbol_type: str):
    """
    Retourne le fichier SVG d'un symbole QElectroTech

    Args:
        symbol_type: Type d'équipement (CBR, DIS, CTR, VTR, PTR)

    Returns:
        Fichier SVG
    """
    # Sécurité : valider le type de symbole
    allowed_symbols = ["CBR", "DIS", "CTR", "VTR", "PTR", "CAP", "REA", "GEN", "BAT", "MOT"]
    if symbol_type.upper() not in allowed_symbols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid symbol type. Allowed: {', '.join(allowed_symbols)}"
        )

    symbol_path = os.path.join(SYMBOLS_DIR, f"{symbol_type.upper()}.svg")

    if not os.path.exists(symbol_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol {symbol_type} not found"
        )

    return FileResponse(
        symbol_path,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
            "Content-Disposition": f"inline; filename={symbol_type}.svg"
        }
    )


@router.post("/reactflow-layout")
async def generate_reactflow_layout(
    request: SLDGenerateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère les données pour ReactFlow avec format compatible Dagre layout

    Cette API retourne la topologie dans le format attendu par ReactFlow :
    - nodes: Liste des équipements avec type et données
    - edges: Liste des connexions entre équipements (via ConnectivityNodes)
    - constraints: Règles RTE pour le layout (busbar horizontal, etc.)

    Le frontend utilisera Dagre pour calculer les positions automatiquement,
    puis l'utilisateur pourra drag-and-drop pour ajuster.

    Args:
        file_id: ID du fichier SCL

    Returns:
        {
            "nodes": [
                {
                    "id": "equipment_id",
                    "type": "equipment",  // custom ReactFlow node type
                    "data": {
                        "label": "CBR_001",
                        "equipmentType": "CBR",
                        "equipmentSubtype": null,
                        "bayName": "Bay1",
                        "voltageLevelName": "VL_400kV"
                    },
                    "position": { "x": 0, "y": 0 }  // Initial position, Dagre will recalculate
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "source": "equipment1_terminal1",
                    "target": "equipment2_terminal1",
                    "data": {
                        "connectivityNode": "CN_BB1"
                    }
                }
            ],
            "constraints": {
                "busbars": [
                    {
                        "id": "BB_400kV",
                        "y": 100,
                        "orientation": "horizontal",
                        "voltageLevelName": "VL_400kV"
                    }
                ],
                "bayOrder": ["Bay1", "Bay2", "CBO", "Bay3"],
                "rteRules": {
                    "busbarHorizontal": true,
                    "bayVertical": true,
                    "equipmentVerticalSpacing": 80
                }
            },
            "statistics": {...}
        }
    """
    file_id = request.file_id

    logger.info(f"Generating ReactFlow layout for file_id={file_id}, user={current_user.username}")

    # 1. Vérifier que le fichier existe
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()
    if not scl_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SCL file with id {file_id} not found"
        )

    # 2. Exécuter les requêtes SPARQL (2 requêtes séparées pour éviter OPTIONAL imbriqués)
    logger.info("Executing SPARQL queries to extract topology")

    # 2.1 Requête principale (topology + equipment)
    query_main = get_sld_complete_query()

    try:
        results = rdf_client.query(scl_file.fuseki_dataset, query_main)
    except Exception as e:
        logger.error(f"Error executing main SPARQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute SPARQL query: {str(e)}"
        )

    logger.info(f"Main SPARQL query returned {len(results)} rows")

    # DEBUG: Count unique equipment in main query (by URI, not name)
    unique_equipment_uris = set()
    unique_equipment_names = set()
    for row in results:
        eq_uri = row.get("equipment", {}).get("value")
        eq_name = row.get("equipmentName", {}).get("value")
        if eq_uri:
            unique_equipment_uris.add(eq_uri)
        if eq_name:
            unique_equipment_names.add(eq_name)

    logger.info(f"DEBUG: Main query contains {len(unique_equipment_uris)} unique equipment URIs from {len(results)} rows")
    logger.info(f"DEBUG: Equipment names (may have duplicates): {sorted(unique_equipment_names)}")

    # 2.2 Requête séparée pour Terminal/ConnectivityNode (évite OPTIONAL imbriqué)
    from app.converters.sld_queries import get_connectivity_query

    query_connectivity = get_connectivity_query()

    try:
        connectivity_results = rdf_client.query(scl_file.fuseki_dataset, query_connectivity)
    except Exception as e:
        logger.warning(f"Connectivity query failed (may be normal if no terminals): {e}")
        connectivity_results = []

    logger.info(f"Connectivity query returned {len(connectivity_results)} rows")

    # Merge results: add terminal data to equipment rows
    # Build a map: equipment_URI -> list of terminals
    terminal_map = {}
    for row in connectivity_results:
        eq_uri = row.get("equipment", {}).get("value")
        if eq_uri:
            if eq_uri not in terminal_map:
                terminal_map[eq_uri] = []
            terminal_map[eq_uri].append(row)

    # Enrich main results with terminal data
    enriched_results = []
    for row in results:
        eq_uri = row.get("equipment", {}).get("value")

        if eq_uri and eq_uri in terminal_map:
            # Create one row per terminal
            for terminal_row in terminal_map[eq_uri]:
                merged_row = {**row}  # Copy main row
                # Add terminal fields
                merged_row["terminalName"] = terminal_row.get("terminalName", {})
                merged_row["terminalCNodeName"] = terminal_row.get("terminalCNodeName", {})
                enriched_results.append(merged_row)
        else:
            # No terminals for this equipment
            enriched_results.append(row)

    logger.info(f"Enriched results: {len(enriched_results)} rows (with terminal data)")

    # DEBUG: Count unique equipment after enrichment
    unique_equipment_enriched_uris = set()
    for row in enriched_results:
        eq_uri = row.get("equipment", {}).get("value")
        if eq_uri:
            unique_equipment_enriched_uris.add(eq_uri)
    logger.info(f"DEBUG: Enriched results contain {len(unique_equipment_enriched_uris)} unique equipment URIs")

    # 3. STEP 1: Extract and validate connectivity topology
    logger.info("=== STEP 1: Extracting ConnectivityNode topology ===")

    from app.sld.connectivity_extractor import extract_connectivity_from_sparql_results

    topology = extract_connectivity_from_sparql_results(enriched_results)

    # Log detailed statistics
    stats = topology.get_statistics()
    logger.info(f"Topology extracted: {stats['equipment_count']} equipment, {stats['edge_count']} edges")
    logger.info(f"ConnectivityNodes: {stats['connectivity_nodes']} total, {stats['connectivity_nodes_with_connections']} with connections")

    # 4. Build ReactFlow nodes from topology (no positions yet)
    logger.info("=== Building ReactFlow nodes from topology ===")

    nodes = []
    edges = []

    # 4.1 Create equipment nodes
    for eq_uri, eq_data in topology.equipment_nodes.items():
        node = {
            "id": eq_uri,  # URI as unique ID
            "type": "equipment",
            "data": {
                "label": eq_data.get("display_name", eq_uri),  # Display name for UI
                "equipmentType": eq_data["type"],
                "equipmentSubtype": eq_data["subtype"],
                "bayName": eq_data["bay_name"],
                "voltageLevelName": eq_data["voltage_level_name"],
                "substationName": eq_data["substation_name"],
                "order": eq_data["order"]
            },
            "position": {"x": 0, "y": 0}  # Will be calculated by Graphviz
        }
        nodes.append(node)

    logger.info(f"Created {len(nodes)} equipment nodes")

    # 4.2 Create busbar nodes
    for busbar_id, busbar_data in topology.busbars.items():
        busbar_node = {
            "id": busbar_id,
            "type": "busbar",
            "data": {
                "label": busbar_data["voltage_level_name"],
                "voltage": busbar_data["voltage"],
                "voltageLevelName": busbar_data["voltage_level_name"]
            },
            "position": {"x": 0, "y": 0}  # Will be calculated by Graphviz
        }
        nodes.append(busbar_node)

    logger.info(f"Created {len(topology.busbars)} busbar nodes, total nodes: {len(nodes)}")

    # 4.3 Create edges from topology
    edge_id = 0
    for eq1, eq2, cn_name in topology.edges:
        edge = {
            "id": f"edge_{edge_id}",
            "source": eq1,
            "target": eq2,
            "data": {
                "connectivityNode": cn_name
            },
            "type": "smoothstep",
            "animated": False
        }
        edges.append(edge)
        edge_id += 1

    logger.info(f"Created {len(edges)} edges")

    # 5. STEP 2: Calculate positions with Graphviz + RTE rules
    logger.info("=== STEP 2: Calculating positions with Graphviz ===")

    from app.sld.graphviz_layout import calculate_layout_with_graphviz

    try:
        nodes_with_positions, edges_final = calculate_layout_with_graphviz(nodes, edges)
        logger.info(f"Graphviz layout calculated: {len(nodes_with_positions)} positioned nodes")
    except Exception as e:
        logger.error(f"Graphviz layout failed: {e}")
        # Fallback: return nodes without calculated positions
        nodes_with_positions = nodes
        edges_final = edges

    # 6. RTE Layout constraints (for reference)
    busbars_list = [
        {
            "id": busbar_id,
            "voltageLevelName": busbar_data["voltage_level_name"],
            "voltage": busbar_data["voltage"]
        }
        for busbar_id, busbar_data in topology.busbars.items()
    ]

    constraints = {
        "busbars": busbars_list,
        "rteRules": {
            "busbarHorizontal": True,
            "bayVertical": True,
            "equipmentVerticalSpacing": 80,
            "bayHorizontalSpacing": 150,
            "busbarVerticalSpacing": 500
        }
    }

    # 7. Statistics
    statistics = {
        "nodes": len(nodes_with_positions),
        "edges": len(edges_final),
        "equipments": stats["equipment_count"],
        "busbars": stats["busbar_count"],
        "connectivityNodes": stats["connectivity_nodes"],
        "connectivityNodesWithConnections": stats["connectivity_nodes_with_connections"],
        "triples_extracted": len(enriched_results)
    }

    logger.info(f"=== ReactFlow layout completed ===")
    logger.info(f"Final statistics: {statistics}")

    return {
        "nodes": nodes_with_positions,
        "edges": edges_final,
        "constraints": constraints,
        "statistics": statistics,
        "file_name": scl_file.filename,
        "generator": "graphviz-backend-v2"
    }


@router.post("/generate")
async def generate_sld_with_powsybl(
    file_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère un schéma unifilaire avec PowSyBl (À VENIR)

    Cette version utilisera :
    1. Conversion IEC 61850 → CIM RDF (via convertisseur)
    2. Export CIM RDF → CGMES XML
    3. PowSyBl pour générer le SVG professionnel

    Args:
        file_id: ID du fichier SCL

    Returns:
        {
            "svg": "<svg>...</svg>",
            "generator": "powsybl"
        }
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PowSyBl integration not yet implemented. Use /generate-simple for now."
    )
