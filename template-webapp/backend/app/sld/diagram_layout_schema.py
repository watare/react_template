"""
DiagramLayout RDF Schema (Named Graph approach)

This module defines the RDF vocabulary for the diagram layout.

Architecture (Option C - Named Graphs):
- Dataset: scl_file_4 (same Fuseki dataset)
  - Named Graph <http://rte.com/iec61850>: IEC 61850 original (READ-ONLY)
  - Named Graph <http://rte.com/diagram_layout>: Positions, symbols, edges (READ-WRITE)

This follows CIM/CGMES standard approach (EQ/DL profiles)

Namespace: http://rte.com/DiagramLayout#

Classes:
- dl:Diagram - Root diagram container
- dl:Node - Equipment node with position and symbol
- dl:Edge - Connection between two nodes (via ConnectivityNode)
- dl:Position - X/Y coordinates for ReactFlow
- dl:Symbol - QElectroTech symbol reference

Properties:
- dl:hasNode - Links diagram to nodes
- dl:hasEdge - Links diagram to edges
- dl:hasPosition - Links node to position
- dl:hasSymbol - Links node to symbol
- dl:x, dl:y - Position coordinates
- dl:symbolType - QElectroTech symbol type (CBR, DIS, etc.)
- dl:source, dl:target - Edge endpoints
- dl:connectivityNode - Reference to IEC 61850 CN

Example RDF:
```turtle
@prefix dl: <http://rte.com/DiagramLayout#> .
@prefix iec: <http://iec61850.com/SCL#> .

:Diagram_file4 a dl:Diagram ;
    dl:hasNode :Node_DJ ;
    dl:hasEdge :Edge_1 .

:Node_DJ a dl:Node ;
    dl:label "DJ" ;
    dl:equipmentType "CBR" ;
    dl:hasPosition :Pos_DJ ;
    dl:hasSymbol :Symbol_CBR ;
    dl:sourceEquipment iec:Equipment_DJ .

:Pos_DJ a dl:Position ;
    dl:x 200.0 ;
    dl:y 150.0 .

:Symbol_CBR a dl:Symbol ;
    dl:symbolType "CBR" ;
    dl:symbolFile "CBR.svg" .

:Edge_1 a dl:Edge ;
    dl:source :Node_DJ ;
    dl:target :Node_SA1 ;
    dl:connectivityNode "POSTE/4/4BUIS1/CN_001" .
```
"""

from rdflib import Namespace, Graph, Literal, URIRef, RDF, RDFS, XSD
from typing import List, Dict, Tuple

# Define namespace
DL = Namespace("http://rte.com/DiagramLayout#")
IEC = Namespace("http://iec61850.com/SCL#")


class DiagramLayoutGraph:
    """
    Builder for DiagramLayout RDF graph

    Creates enriched RDF mirror with:
    - Equipment nodes with positions and symbols
    - Edges with connectivity information
    - Layout metadata (RTE rules, statistics)
    """

    def __init__(self, diagram_id: str):
        """
        Initialize DiagramLayout graph

        Args:
            diagram_id: Unique identifier for this diagram (e.g., "file_4")
        """
        self.graph = Graph()
        self.graph.bind("dl", DL)
        self.graph.bind("iec", IEC)
        self.graph.bind("xsd", XSD)

        self.diagram_id = diagram_id
        self.diagram_uri = DL[f"Diagram_{diagram_id}"]

        # Create diagram root
        self.graph.add((self.diagram_uri, RDF.type, DL.Diagram))
        self.graph.add((self.diagram_uri, RDFS.label, Literal(f"SLD Diagram {diagram_id}")))

        self.node_count = 0
        self.edge_count = 0

    def add_equipment_node(
        self,
        equipment_id: str,
        label: str,
        equipment_type: str,
        position: Tuple[float, float],
        bay_name: str,
        voltage_level_name: str,
        substation_name: str,
        equipment_subtype: str = None,
        symbol_type: str = None
    ) -> URIRef:
        """
        Add equipment node to diagram

        Args:
            equipment_id: Unique equipment identifier (from IEC 61850)
            label: Display label
            equipment_type: CBR, DIS, CTR, VTR, PTR, etc.
            position: (x, y) coordinates
            bay_name: Bay name
            voltage_level_name: Voltage level name
            substation_name: Substation name
            equipment_subtype: Optional subtype (SA, SL, ST, SS for DIS)
            symbol_type: Optional symbol override

        Returns:
            URIRef of created node
        """
        node_uri = DL[f"Node_{equipment_id}"]
        pos_uri = DL[f"Pos_{equipment_id}"]

        # Node
        self.graph.add((self.diagram_uri, DL.hasNode, node_uri))
        self.graph.add((node_uri, RDF.type, DL.Node))
        self.graph.add((node_uri, RDFS.label, Literal(label)))
        self.graph.add((node_uri, DL.equipmentType, Literal(equipment_type)))

        if equipment_subtype:
            self.graph.add((node_uri, DL.equipmentSubtype, Literal(equipment_subtype)))

        self.graph.add((node_uri, DL.bayName, Literal(bay_name)))
        self.graph.add((node_uri, DL.voltageLevelName, Literal(voltage_level_name)))
        self.graph.add((node_uri, DL.substationName, Literal(substation_name)))

        # Link to source IEC 61850 equipment
        self.graph.add((node_uri, DL.sourceEquipment, IEC[equipment_id]))

        # Position
        self.graph.add((node_uri, DL.hasPosition, pos_uri))
        self.graph.add((pos_uri, RDF.type, DL.Position))
        self.graph.add((pos_uri, DL.x, Literal(position[0], datatype=XSD.double)))
        self.graph.add((pos_uri, DL.y, Literal(position[1], datatype=XSD.double)))

        # Symbol
        symbol_ref = symbol_type or equipment_type
        symbol_uri = DL[f"Symbol_{symbol_ref}"]
        self.graph.add((node_uri, DL.hasSymbol, symbol_uri))
        self.graph.add((symbol_uri, RDF.type, DL.Symbol))
        self.graph.add((symbol_uri, DL.symbolType, Literal(symbol_ref)))
        self.graph.add((symbol_uri, DL.symbolFile, Literal(f"{symbol_ref}.svg")))

        self.node_count += 1
        return node_uri

    def add_busbar_node(
        self,
        busbar_id: str,
        label: str,
        position: Tuple[float, float],
        voltage_level_name: str,
        voltage: str = None
    ) -> URIRef:
        """
        Add busbar node to diagram

        Args:
            busbar_id: Unique busbar identifier
            label: Display label
            position: (x, y) coordinates
            voltage_level_name: Voltage level name
            voltage: Optional voltage value

        Returns:
            URIRef of created busbar node
        """
        node_uri = DL[f"Node_{busbar_id}"]
        pos_uri = DL[f"Pos_{busbar_id}"]

        # Node
        self.graph.add((self.diagram_uri, DL.hasNode, node_uri))
        self.graph.add((node_uri, RDF.type, DL.BusbarNode))
        self.graph.add((node_uri, RDFS.label, Literal(label)))
        self.graph.add((node_uri, DL.voltageLevelName, Literal(voltage_level_name)))

        if voltage:
            self.graph.add((node_uri, DL.voltage, Literal(voltage)))

        # Position
        self.graph.add((node_uri, DL.hasPosition, pos_uri))
        self.graph.add((pos_uri, RDF.type, DL.Position))
        self.graph.add((pos_uri, DL.x, Literal(position[0], datatype=XSD.double)))
        self.graph.add((pos_uri, DL.y, Literal(position[1], datatype=XSD.double)))

        self.node_count += 1
        return node_uri

    def add_edge(
        self,
        edge_id: str,
        source_node_id: str,
        target_node_id: str,
        connectivity_node_name: str
    ) -> URIRef:
        """
        Add edge (connection) between two nodes

        Args:
            edge_id: Unique edge identifier
            source_node_id: Source equipment ID
            target_node_id: Target equipment ID
            connectivity_node_name: ConnectivityNode name from IEC 61850

        Returns:
            URIRef of created edge
        """
        edge_uri = DL[f"Edge_{edge_id}"]
        source_uri = DL[f"Node_{source_node_id}"]
        target_uri = DL[f"Node_{target_node_id}"]

        # Edge
        self.graph.add((self.diagram_uri, DL.hasEdge, edge_uri))
        self.graph.add((edge_uri, RDF.type, DL.Edge))
        self.graph.add((edge_uri, DL.source, source_uri))
        self.graph.add((edge_uri, DL.target, target_uri))
        self.graph.add((edge_uri, DL.connectivityNode, Literal(connectivity_node_name)))

        self.edge_count += 1
        return edge_uri

    def add_metadata(self, metadata: Dict):
        """
        Add diagram metadata (statistics, generator info, etc.)

        Args:
            metadata: Dictionary with metadata
        """
        for key, value in metadata.items():
            self.graph.add((self.diagram_uri, DL[key], Literal(str(value))))

    def to_turtle(self) -> str:
        """
        Serialize graph to Turtle format

        Returns:
            Turtle string
        """
        return self.graph.serialize(format='turtle')

    def to_json_ld(self) -> str:
        """
        Serialize graph to JSON-LD format

        Returns:
            JSON-LD string
        """
        return self.graph.serialize(format='json-ld', indent=2)

    def get_statistics(self) -> Dict:
        """
        Get diagram statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "nodes": self.node_count,
            "edges": self.edge_count
        }
