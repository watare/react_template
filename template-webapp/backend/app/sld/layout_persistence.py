"""
Layout Persistence Layer - Save/Load diagram layouts to/from RDF

This module handles:
- Converting layout data to SPARQL INSERT statements
- Saving equipment positions to DiagramLayout RDF
- Saving connection paths to DiagramLayout RDF
- Generating unique URIs for diagram objects
"""

from typing import Dict, List
from uuid import uuid4
from app.rdf.layout_queries import (
    create_diagram_layout_insert,
    create_equipment_position_insert
)


class LayoutPersistence:
    """
    Persistence layer for diagram layouts

    Converts layout data structure (from LayoutEngine) to SPARQL updates
    that persist positions and connections to the DiagramLayout RDF graph
    """

    def __init__(self, base_uri: str = "http://vpac.energy/diagram/"):
        self.base_uri = base_uri

    def generate_diagram_uri(self, diagram_name: str) -> str:
        """Generate unique URI for a diagram"""
        return f"{self.base_uri}{diagram_name}"

    def generate_diagram_object_uri(self, diagram_name: str, equipment_name: str) -> str:
        """Generate unique URI for a diagram object"""
        return f"{self.base_uri}{diagram_name}/object/{equipment_name}"

    def generate_point_uri(self, diagram_name: str, equipment_name: str, point_index: int = 0) -> str:
        """Generate unique URI for a diagram object point"""
        return f"{self.base_uri}{diagram_name}/point/{equipment_name}_{point_index}"

    def generate_connection_uri(self, diagram_name: str, from_eq: str, to_eq: str) -> str:
        """Generate unique URI for a connection"""
        safe_from = from_eq.replace(" ", "_")
        safe_to = to_eq.replace(" ", "_")
        return f"{self.base_uri}{diagram_name}/connection/{safe_from}_{safe_to}"

    def build_insert_queries(self, diagram_name: str, layout_data: Dict) -> List[str]:
        """
        Build SPARQL INSERT queries from layout data

        Args:
            diagram_name: Name of the diagram
            layout_data: Output from LayoutEngine.generate_layout()

        Returns:
            List of SPARQL INSERT queries to execute
        """
        queries = []

        # 1. Create diagram
        diagram_uri = self.generate_diagram_uri(diagram_name)
        queries.append(create_diagram_layout_insert(
            diagram_name=diagram_name,
            diagram_uri=diagram_uri,
            orientation="vertical"
        ))

        # 2. Create equipment positions
        bay_indices = {}  # Track bay indices
        vl_indices = {}   # Track voltage level indices

        for eq_data in layout_data.get("equipments", []):
            equipment_name = eq_data["name"]
            equipment_type = eq_data["type"]
            bay_name = eq_data.get("bay_name", "")
            vl_name = eq_data.get("voltage_level_name", "")

            # Track indices for ordering
            if vl_name not in vl_indices:
                vl_indices[vl_name] = len(vl_indices)
            if bay_name not in bay_indices:
                bay_indices[bay_name] = len(bay_indices)

            # Generate URIs
            # Note: equipment_uri should come from IEC 61850 RDF
            # For now, we use a placeholder - this should be resolved by looking up
            # the equipment in the IEC 61850 graph
            equipment_uri = f"http://iec61850.com/equipment/{equipment_name}"
            diagram_object_uri = self.generate_diagram_object_uri(diagram_name, equipment_name)
            point_uri = self.generate_point_uri(diagram_name, equipment_name)

            queries.append(create_equipment_position_insert(
                diagram_uri=diagram_uri,
                equipment_uri=equipment_uri,
                diagram_object_uri=diagram_object_uri,
                point_uri=point_uri,
                x_position=eq_data["x"],
                y_position=eq_data["y"],
                rotation=eq_data.get("rotation", 0.0),
                bay_index=bay_indices.get(bay_name),
                vl_index=vl_indices.get(vl_name),
                drawing_order=10
            ))

        # 3. Create busbar positions
        for bb_data in layout_data.get("busbars", []):
            busbar_name = bb_data["name"]
            busbar_uri = f"http://iec61850.com/busbar/{busbar_name}"
            diagram_object_uri = self.generate_diagram_object_uri(diagram_name, busbar_name)

            # Busbars are represented as horizontal lines
            # Store start and end points
            point_start_uri = self.generate_point_uri(diagram_name, busbar_name, 0)
            point_end_uri = self.generate_point_uri(diagram_name, busbar_name, 1)

            # Start point
            queries.append(create_equipment_position_insert(
                diagram_uri=diagram_uri,
                equipment_uri=busbar_uri,
                diagram_object_uri=diagram_object_uri,
                point_uri=point_start_uri,
                x_position=bb_data["x_start"],
                y_position=bb_data["y"],
                rotation=0.0,
                drawing_order=1  # Busbars drawn first
            ))

            # End point (for line rendering)
            queries.append(f"""
            PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                <{point_end_uri}> a dl:DiagramObjectPoint ;
                    dl:xPosition "{bb_data['x_end']}"^^xsd:float ;
                    dl:yPosition "{bb_data['y']}"^^xsd:float ;
                    dl:sequenceNumber 1 .

                <{diagram_object_uri}> dl:diagramObjectPoints <{point_end_uri}> .
            }}
            """)

        # 4. Create connections with paths
        for conn_data in layout_data.get("connections", []):
            from_eq = conn_data["from_equipment"]
            to_eq = conn_data["to_equipment"]
            path = conn_data.get("path", [])

            if len(path) < 2:
                continue  # Skip invalid connections

            connection_uri = self.generate_connection_uri(diagram_name, from_eq, to_eq)
            diagram_object_uri = self.generate_diagram_object_uri(diagram_name, f"conn_{from_eq}_{to_eq}")

            # Create connection object
            queries.append(f"""
            PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            INSERT DATA {{
                <{diagram_object_uri}> a dl:DiagramObject ;
                    dl:diagram <{diagram_uri}> ;
                    dl:drawingOrder 5 .
            }}
            """)

            # Add all path points
            for i, point in enumerate(path):
                point_uri = self.generate_point_uri(diagram_name, f"conn_{from_eq}_{to_eq}", i)
                queries.append(f"""
                PREFIX dl: <http://vpac.energy/ontology/diagram-layout#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                INSERT DATA {{
                    <{point_uri}> a dl:DiagramObjectPoint ;
                        dl:xPosition "{point['x']}"^^xsd:float ;
                        dl:yPosition "{point['y']}"^^xsd:float ;
                        dl:sequenceNumber {i} .

                    <{diagram_object_uri}> dl:diagramObjectPoints <{point_uri}> .
                }}
                """)

        return queries

    def save_layout(self, fuseki_client, diagram_name: str, layout_data: Dict, dataset: str = "vpac"):
        """
        Save layout data to Fuseki triplestore

        Args:
            fuseki_client: FusekiClient instance
            diagram_name: Name of the diagram
            layout_data: Output from LayoutEngine.generate_layout()
            dataset: Fuseki dataset name
        """
        queries = self.build_insert_queries(diagram_name, layout_data)

        for query in queries:
            fuseki_client.update(query, dataset=dataset)

        return {
            "diagram_uri": self.generate_diagram_uri(diagram_name),
            "equipment_count": len(layout_data.get("equipments", [])),
            "connection_count": len(layout_data.get("connections", [])),
            "busbar_count": len(layout_data.get("busbars", []))
        }


def generate_and_persist_layout(
    fuseki_client,
    diagram_name: str,
    topology_data: Dict,
    dataset: str = "vpac"
) -> Dict:
    """
    Helper function to generate layout and persist it to RDF

    Args:
        fuseki_client: FusekiClient instance
        diagram_name: Name of the diagram
        topology_data: SPARQL results from get_sld_complete_query()
        dataset: Fuseki dataset name

    Returns:
        Persistence result with diagram URI and statistics
    """
    from app.sld.layout_engine import LayoutEngine

    # Generate layout
    engine = LayoutEngine()
    layout_data = engine.generate_layout(topology_data)

    # Persist to RDF
    persistence = LayoutPersistence()
    result = persistence.save_layout(fuseki_client, diagram_name, layout_data, dataset)

    return result
