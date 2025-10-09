"""
Layout Engine for Single Line Diagrams

This module implements the automatic layout algorithm for SLD generation:
1. Read topology from IEC 61850 RDF
2. Apply RTE layout rules (rte_rules.py)
3. Calculate positions (x, y) for each equipment
4. Identify real connections via ConnectivityNodes
5. Route connection lines (straight, Manhattan, angles)
6. Persist to DiagramLayout RDF

Architecture:
    IEC 61850 RDF → Layout Algorithm → DiagramLayout RDF → Frontend

Key concepts:
    - Equipment positioning: Vertical stacking within bays, horizontal spacing between bays
    - Connection routing: Manhattan routing (horizontal + vertical segments only)
    - ConnectivityNode: Represents electrical connection point (busbar, junction)
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
import logging
from app.sld.rte_rules import RTERenderingNamespace, RTELayoutRules

logger = logging.getLogger(__name__)


@dataclass
class Point:
    """2D coordinate point"""
    x: float
    y: float

    def __repr__(self):
        return f"({self.x}, {self.y})"


@dataclass
class Terminal:
    """Equipment terminal with position and connectivity"""
    equipment_name: str
    terminal_name: str
    connectivity_node: str  # ConnectivityNode name
    position: Point = None  # Calculated position (x, y)
    orientation: str = "n"  # n, s, e, w


@dataclass
class Connection:
    """Connection between two terminals"""
    from_terminal: Terminal
    to_terminal: Terminal
    path: List[Point] = field(default_factory=list)  # Routed path with waypoints

    def __repr__(self):
        return f"{self.from_terminal.equipment_name}.{self.from_terminal.terminal_name} → {self.to_terminal.equipment_name}.{self.to_terminal.terminal_name}"


@dataclass
class EquipmentLayout:
    """Positioned equipment with calculated coordinates"""
    name: str
    type: str
    subtype: Optional[str]
    position: Point
    rotation: float = 0.0  # Degrees (0 = vertical, 90 = horizontal)
    terminals: List[Terminal] = field(default_factory=list)
    bay_name: str = ""
    voltage_level_name: str = ""


@dataclass
class BusbarLayout:
    """Busbar (jeu de barres) layout"""
    name: str
    voltage_level: str
    y_position: float  # Horizontal line at fixed Y
    x_start: float
    x_end: float
    connectivity_node: str  # ConnectivityNode representing the busbar


class LayoutEngine:
    """
    Layout Engine for Single Line Diagrams

    Responsibilities:
    - Calculate equipment positions based on RTE rules
    - Identify connections via ConnectivityNodes
    - Route connection lines (Manhattan routing)
    - Generate DiagramLayout RDF
    """

    def __init__(self, rte_rules: Optional[RTELayoutRules] = None):
        self.rules = rte_rules or RTELayoutRules()
        self.rte_namespace = RTERenderingNamespace()

        # Layout state
        self.equipments: Dict[str, EquipmentLayout] = {}
        self.terminals: Dict[str, Terminal] = {}  # terminal_name → Terminal
        self.connectivity_nodes: Dict[str, List[Terminal]] = {}  # cn_name → [terminals]
        self.connections: List[Connection] = []
        self.busbars: List[BusbarLayout] = []

    def generate_layout(self, topology_data: Dict) -> Dict:
        """
        Generate layout from IEC 61850 topology data

        Args:
            topology_data: Result from SPARQL query (get_sld_complete_query)

        Returns:
            Layout data ready for DiagramLayout RDF persistence
        """
        logger.info("Starting layout generation")

        # 1. Parse topology data
        self._parse_topology(topology_data)

        # 2. Calculate equipment positions
        self._calculate_positions()

        # 3. Calculate terminal positions
        self._calculate_terminal_positions()

        # 4. Identify connections via ConnectivityNodes
        self._identify_connections()

        # 5. Route connection lines
        self._route_connections()

        # 6. Generate layout data
        layout_data = self._build_layout_data()

        logger.info(f"Layout generated: {len(self.equipments)} equipments, {len(self.connections)} connections")

        return layout_data

    def _parse_topology(self, topology_data: Dict):
        """Parse SPARQL query results into internal data structures"""

        # Group data by substation → voltage level → bay → equipment
        hierarchy = {}

        for row in topology_data.get("results", []):
            substation_name = row.get("substationName", {}).get("value")
            vl_name = row.get("voltageLevelName", {}).get("value")
            bay_name = row.get("bayName", {}).get("value")
            equipment_name = row.get("equipmentName", {}).get("value")

            if not all([substation_name, vl_name, bay_name]):
                continue

            # Initialize hierarchy
            if substation_name not in hierarchy:
                hierarchy[substation_name] = {}
            if vl_name not in hierarchy[substation_name]:
                hierarchy[substation_name][vl_name] = {}
            if bay_name not in hierarchy[substation_name][vl_name]:
                hierarchy[substation_name][vl_name][bay_name] = []

            # Add equipment if present
            if equipment_name:
                equipment_type = row.get("equipmentType", {}).get("value")
                equipment_subtype = row.get("equipmentSubtype", {}).get("value")
                equipment_order = row.get("equipmentOrder", {}).get("value", 999)

                # Terminal data
                terminal_name = row.get("terminalName", {}).get("value")
                terminal_cn = row.get("terminalCNodeName", {}).get("value")

                equipment_data = {
                    "name": equipment_name,
                    "type": equipment_type,
                    "subtype": equipment_subtype,
                    "order": int(equipment_order) if equipment_order else 999,
                    "bay_name": bay_name,
                    "voltage_level_name": vl_name,
                    "terminals": []
                }

                # Add terminal if present
                if terminal_name and terminal_cn:
                    terminal = Terminal(
                        equipment_name=equipment_name,
                        terminal_name=terminal_name,
                        connectivity_node=terminal_cn
                    )
                    equipment_data["terminals"].append(terminal)

                    # Index terminal
                    terminal_key = f"{equipment_name}.{terminal_name}"
                    self.terminals[terminal_key] = terminal

                    # Group by connectivity node
                    if terminal_cn not in self.connectivity_nodes:
                        self.connectivity_nodes[terminal_cn] = []
                    self.connectivity_nodes[terminal_cn].append(terminal)

                hierarchy[substation_name][vl_name][bay_name].append(equipment_data)

        self.hierarchy = hierarchy
        logger.info(f"Parsed topology: {len(hierarchy)} substations")

    def _calculate_positions(self):
        """
        Calculate (x, y) positions for all equipment using RTE rules

        Layout strategy:
        - Voltage levels stacked vertically (y-axis)
        - Bays arranged horizontally within voltage level (x-axis)
        - Equipment stacked vertically within bay
        """

        current_y = self.rules.busbar_vertical_spacing  # Start below top margin
        vl_index = 0

        for substation_name, voltage_levels in self.hierarchy.items():
            for vl_name, bays in voltage_levels.items():
                # Create busbar for this voltage level
                busbar_y = current_y
                busbar_x_start = self.rules.bay_horizontal_spacing

                # Calculate busbar length (based on number of bays)
                num_bays = len(bays)
                busbar_x_end = busbar_x_start + num_bays * (100 + self.rules.bay_horizontal_spacing)

                busbar = BusbarLayout(
                    name=f"{vl_name}_BUSBAR",
                    voltage_level=vl_name,
                    y_position=busbar_y,
                    x_start=busbar_x_start,
                    x_end=busbar_x_end,
                    connectivity_node=f"{vl_name}_BB"  # Convention: BB = Busbar
                )
                self.busbars.append(busbar)

                # Position bays horizontally
                current_x = busbar_x_start
                bay_index = 0

                for bay_name, equipments in bays.items():
                    # Sort equipment by order (from SCD file)
                    equipments_sorted = sorted(equipments, key=lambda e: (e["order"], e["name"]))

                    # Position equipment vertically within bay
                    equipment_y = busbar_y + 80  # Start below busbar

                    for eq_data in equipments_sorted:
                        equipment = EquipmentLayout(
                            name=eq_data["name"],
                            type=eq_data["type"],
                            subtype=eq_data["subtype"],
                            position=Point(current_x, equipment_y),
                            rotation=0.0,  # Vertical by default
                            terminals=eq_data["terminals"],
                            bay_name=bay_name,
                            voltage_level_name=vl_name
                        )

                        self.equipments[eq_data["name"]] = equipment

                        # Move down for next equipment
                        equipment_y += self.rules.equipment_vertical_spacing

                    # Move right for next bay
                    current_x += 100 + self.rules.bay_horizontal_spacing
                    bay_index += 1

                # Move down for next voltage level
                current_y += self.rules.busbar_vertical_spacing + 400  # Space between VLs
                vl_index += 1

    def _calculate_terminal_positions(self):
        """Calculate absolute (x, y) positions for all terminals"""

        # TODO: Load terminal positions from symbol metadata (QElectroTech)
        # For now, use simple top/bottom positioning

        for equipment in self.equipments.values():
            num_terminals = len(equipment.terminals)

            if num_terminals == 0:
                continue

            # Simple strategy: distribute terminals vertically
            # Top terminal(s) = north, bottom terminal(s) = south
            for i, terminal in enumerate(equipment.terminals):
                if i < num_terminals / 2:
                    # Top terminal (north)
                    terminal.position = Point(
                        equipment.position.x,
                        equipment.position.y - 30  # 30px above equipment center
                    )
                    terminal.orientation = "n"
                else:
                    # Bottom terminal (south)
                    terminal.position = Point(
                        equipment.position.x,
                        equipment.position.y + 30  # 30px below equipment center
                    )
                    terminal.orientation = "s"

    def _identify_connections(self):
        """
        Identify real electrical connections via ConnectivityNodes

        A connection exists when 2+ terminals share the same ConnectivityNode
        """

        for cn_name, terminals in self.connectivity_nodes.items():
            if len(terminals) < 2:
                continue  # No connection if only 1 terminal

            # Create connections between all pairs of terminals on this node
            # (mesh topology)
            for i in range(len(terminals) - 1):
                for j in range(i + 1, len(terminals)):
                    connection = Connection(
                        from_terminal=terminals[i],
                        to_terminal=terminals[j]
                    )
                    self.connections.append(connection)

        logger.info(f"Identified {len(self.connections)} connections from {len(self.connectivity_nodes)} connectivity nodes")

    def _route_connections(self):
        """
        Route connection lines using Manhattan routing (orthogonal lines only)

        Strategy:
        - Straight vertical line if terminals are vertically aligned
        - Manhattan routing (H-V-H or V-H-V) otherwise
        - Avoid overlapping equipment
        """

        for connection in self.connections:
            from_pos = connection.from_terminal.position
            to_pos = connection.to_terminal.position

            if not from_pos or not to_pos:
                continue

            # Simple strategy: straight line for now
            # TODO: Implement proper Manhattan routing with obstacle avoidance
            connection.path = [from_pos, to_pos]

    def _build_layout_data(self) -> Dict:
        """
        Build layout data structure for DiagramLayout RDF persistence

        Returns:
            {
                "equipments": [{name, type, x, y, rotation, terminals}, ...],
                "connections": [{from_terminal, to_terminal, path}, ...],
                "busbars": [{name, y, x_start, x_end}, ...]
            }
        """

        return {
            "equipments": [
                {
                    "name": eq.name,
                    "type": eq.type,
                    "subtype": eq.subtype,
                    "x": eq.position.x,
                    "y": eq.position.y,
                    "rotation": eq.rotation,
                    "bay_name": eq.bay_name,
                    "voltage_level_name": eq.voltage_level_name,
                    "terminals": [
                        {
                            "name": t.terminal_name,
                            "connectivity_node": t.connectivity_node,
                            "x": t.position.x if t.position else 0,
                            "y": t.position.y if t.position else 0,
                            "orientation": t.orientation
                        }
                        for t in eq.terminals
                    ]
                }
                for eq in self.equipments.values()
            ],
            "connections": [
                {
                    "from_equipment": conn.from_terminal.equipment_name,
                    "from_terminal": conn.from_terminal.terminal_name,
                    "to_equipment": conn.to_terminal.equipment_name,
                    "to_terminal": conn.to_terminal.terminal_name,
                    "connectivity_node": conn.from_terminal.connectivity_node,
                    "path": [{"x": p.x, "y": p.y} for p in conn.path]
                }
                for conn in self.connections
            ],
            "busbars": [
                {
                    "name": bb.name,
                    "voltage_level": bb.voltage_level,
                    "y": bb.y_position,
                    "x_start": bb.x_start,
                    "x_end": bb.x_end,
                    "connectivity_node": bb.connectivity_node
                }
                for bb in self.busbars
            ]
        }


def generate_layout_from_topology(topology_data: Dict) -> Dict:
    """
    Helper function to generate layout from IEC 61850 topology

    Args:
        topology_data: SPARQL query results from get_sld_complete_query()

    Returns:
        Layout data ready for DiagramLayout RDF persistence
    """
    engine = LayoutEngine()
    return engine.generate_layout(topology_data)
