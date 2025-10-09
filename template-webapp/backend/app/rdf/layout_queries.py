"""
SPARQL Queries for Diagram Layout Persistence

These queries handle:
- Saving equipment positions to RDF
- Loading equipment positions from RDF
- Updating positions when user drags equipment
- Generating initial layout from IEC 61850 topology
"""

from typing import Dict, List, Optional


def get_equipment_positions_query(diagram_name: str) -> str:
    """
    Retrieve all equipment positions for a given diagram

    Returns: List of equipment with their x, y positions
    """
    return f"""
    PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>
    PREFIX cim: <http://iec.ch/TC57/CIM100#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?equipmentName ?equipmentURI ?xPosition ?yPosition ?rotation ?bayIndex ?vlIndex
    WHERE {{
        ?diagram a dl:Diagram ;
                 dl:diagramName "{diagram_name}" .

        ?diagramObject a dl:DiagramObject ;
                      dl:diagram ?diagram ;
                      dl:identifiedObject ?equipmentURI ;
                      dl:diagramObjectPoints ?point .

        ?equipmentURI cim:IdentifiedObject.name ?equipmentName .

        ?point dl:xPosition ?xPosition ;
               dl:yPosition ?yPosition ;
               dl:sequenceNumber 0 .

        OPTIONAL {{ ?diagramObject dl:rotation ?rotation . }}
        OPTIONAL {{ ?diagramObject dl:bayIndex ?bayIndex . }}
        OPTIONAL {{ ?diagramObject dl:voltageLevelIndex ?vlIndex . }}
    }}
    ORDER BY ?vlIndex ?bayIndex
    """


def save_equipment_position_update(
    diagram_name: str,
    equipment_uri: str,
    x_position: float,
    y_position: float,
    rotation: float = 0.0
) -> str:
    """
    Update the position of an equipment in the diagram

    Used when user drags an equipment to a new position
    """
    return f"""
    PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>
    PREFIX cim: <http://iec.ch/TC57/CIM100#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE {{
        ?point dl:xPosition ?oldX ;
               dl:yPosition ?oldY .
        ?diagramObject dl:rotation ?oldRotation .
    }}
    INSERT {{
        ?point dl:xPosition "{x_position}"^^xsd:float ;
               dl:yPosition "{y_position}"^^xsd:float .
        ?diagramObject dl:rotation "{rotation}"^^xsd:float .
    }}
    WHERE {{
        ?diagram a dl:Diagram ;
                 dl:diagramName "{diagram_name}" .

        ?diagramObject a dl:DiagramObject ;
                      dl:diagram ?diagram ;
                      dl:identifiedObject <{equipment_uri}> ;
                      dl:diagramObjectPoints ?point .

        ?point dl:sequenceNumber 0 ;
               dl:xPosition ?oldX ;
               dl:yPosition ?oldY .

        OPTIONAL {{ ?diagramObject dl:rotation ?oldRotation . }}
    }}
    """


def create_diagram_layout_insert(
    diagram_name: str,
    diagram_uri: str,
    orientation: str = "vertical"
) -> str:
    """
    Create a new diagram layout (canvas)

    Called when first generating SLD for a substation
    """
    return f"""
    PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>
    PREFIX cim: <http://iec.ch/TC57/CIM100#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        <{diagram_uri}> a dl:Diagram ;
            dl:diagramName "{diagram_name}" ;
            dl:orientation "{orientation}" ;
            cim:IdentifiedObject.name "{diagram_name}" .
    }}
    """


def create_equipment_position_insert(
    diagram_uri: str,
    equipment_uri: str,
    diagram_object_uri: str,
    point_uri: str,
    x_position: float,
    y_position: float,
    rotation: float = 0.0,
    bay_index: Optional[int] = None,
    vl_index: Optional[int] = None,
    drawing_order: int = 10
) -> str:
    """
    Insert a new equipment position into the diagram

    Called when:
    - Generating initial layout from IEC 61850 topology
    - User manually adds equipment to diagram
    """
    bay_index_triple = f"dl:bayIndex {bay_index} ;" if bay_index is not None else ""
    vl_index_triple = f"dl:voltageLevelIndex {vl_index} ;" if vl_index is not None else ""

    return f"""
    PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {{
        <{diagram_object_uri}> a dl:DiagramObject ;
            dl:diagram <{diagram_uri}> ;
            dl:identifiedObject <{equipment_uri}> ;
            dl:rotation "{rotation}"^^xsd:float ;
            dl:drawingOrder {drawing_order} ;
            {bay_index_triple}
            {vl_index_triple}
            dl:diagramObjectPoints <{point_uri}> .

        <{point_uri}> a dl:DiagramObjectPoint ;
            dl:xPosition "{x_position}"^^xsd:float ;
            dl:yPosition "{y_position}"^^xsd:float ;
            dl:sequenceNumber 0 .
    }}
    """


def delete_equipment_from_diagram(
    diagram_name: str,
    equipment_uri: str
) -> str:
    """
    Remove an equipment from the diagram

    Used when user deletes equipment from visual editor
    """
    return f"""
    PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>

    DELETE {{
        ?diagramObject ?p1 ?o1 .
        ?point ?p2 ?o2 .
    }}
    WHERE {{
        ?diagram a dl:Diagram ;
                 dl:diagramName "{diagram_name}" .

        ?diagramObject a dl:DiagramObject ;
                      dl:diagram ?diagram ;
                      dl:identifiedObject <{equipment_uri}> ;
                      ?p1 ?o1 .

        OPTIONAL {{
            ?diagramObject dl:diagramObjectPoints ?point .
            ?point ?p2 ?o2 .
        }}
    }}
    """


def get_diagram_bounding_box_query(diagram_name: str) -> str:
    """
    Calculate the bounding box of all equipment in the diagram

    Used for:
    - Auto-fitting viewport
    - Calculating canvas size
    """
    return f"""
    PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>

    SELECT (MIN(?x) AS ?minX) (MAX(?x) AS ?maxX) (MIN(?y) AS ?minY) (MAX(?y) AS ?maxY)
    WHERE {{
        ?diagram a dl:Diagram ;
                 dl:diagramName "{diagram_name}" .

        ?diagramObject a dl:DiagramObject ;
                      dl:diagram ?diagram ;
                      dl:diagramObjectPoints ?point .

        ?point dl:xPosition ?x ;
               dl:yPosition ?y .
    }}
    """


def check_diagram_exists_query(diagram_name: str) -> str:
    """
    Check if a diagram with given name already exists
    """
    return f"""
    PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>

    ASK {{
        ?diagram a dl:Diagram ;
                 dl:diagramName "{diagram_name}" .
    }}
    """


def get_all_diagrams_query() -> str:
    """
    Get list of all saved diagrams
    """
    return """
    PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>

    SELECT ?diagramURI ?diagramName ?orientation
    WHERE {
        ?diagramURI a dl:Diagram ;
                    dl:diagramName ?diagramName .

        OPTIONAL { ?diagramURI dl:orientation ?orientation . }
    }
    ORDER BY ?diagramName
    """
