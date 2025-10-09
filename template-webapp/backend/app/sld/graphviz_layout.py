"""
Graphviz Layout Engine for Single Line Diagrams

Uses Graphviz 'dot' algorithm to calculate professional layouts
Returns positions ready for ReactFlow frontend
"""

import logging
import subprocess
import json
import tempfile
from typing import Dict, List, Tuple
import networkx as nx

logger = logging.getLogger(__name__)


class GraphvizLayoutEngine:
    """
    Professional layout engine using Graphviz

    Calculates equipment positions using industry-standard graph algorithms
    Applies RTE rules (busbars horizontal, bays vertical)
    Returns positions in ReactFlow format
    """

    def __init__(self):
        self.rte_rules = {
            'busbar_horizontal': True,
            'bay_vertical': True,
            'equipment_vertical_spacing': 80,
            'bay_horizontal_spacing': 150,
            'busbar_vertical_spacing': 500,
        }

    def calculate_layout(
        self,
        nodes: List[Dict],
        edges: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Calculate layout positions using Graphviz

        Args:
            nodes: List of equipment/busbar nodes (id, type, data)
            edges: List of connections (source, target)

        Returns:
            (nodes_with_positions, edges)
        """

        if not nodes:
            logger.warning("No nodes to layout")
            return [], []

        logger.info(f"Calculating layout for {len(nodes)} nodes, {len(edges)} edges")

        # Create NetworkX graph
        G = nx.DiGraph()

        # Add nodes with metadata
        for node in nodes:
            node_id = node['id']
            node_type = node.get('type', 'equipment')

            # Set node size for Graphviz
            if node_type == 'busbar':
                width = 8  # Busbars are wide
                height = 0.5
            else:
                width = 1.5
                height = 1.5

            G.add_node(
                node_id,
                width=width,
                height=height,
                node_type=node_type,
                data=node.get('data', {})
            )

        # Add edges
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source and target:
                G.add_edge(source, target)

        logger.info(f"Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        # Calculate layout using Graphviz 'dot' executable directly
        try:
            pos = self._run_graphviz_dot(G)
            logger.info(f"Graphviz layout calculated: {len(pos)} positions")
        except Exception as e:
            logger.error(f"Graphviz layout failed: {e}")
            # Fallback to simple grid layout
            pos = self._fallback_grid_layout(nodes)

        # Apply RTE constraints
        pos_adjusted = self._apply_rte_constraints(nodes, pos, G)

        # Build ReactFlow nodes with positions
        nodes_with_positions = []
        for node in nodes:
            node_id = node['id']
            if node_id in pos_adjusted:
                x, y = pos_adjusted[node_id]
                node_copy = node.copy()
                node_copy['position'] = {'x': x, 'y': y}
                nodes_with_positions.append(node_copy)

                # Log sample positions for debugging
                if len(nodes_with_positions) <= 3:
                    logger.info(f"Sample position: {node_id} at ({x:.1f}, {y:.1f})")
            else:
                logger.warning(f"Node {node_id} has no position")
                node_copy = node.copy()
                node_copy['position'] = {'x': 0, 'y': 0}
                nodes_with_positions.append(node_copy)

        logger.info(f"Layout complete: {len(nodes_with_positions)} positioned nodes")

        return nodes_with_positions, edges

    def _run_graphviz_dot(self, G: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
        """
        Run Graphviz 'dot' executable directly to calculate layout

        This avoids the complexity of PyGraphviz installation
        Calls: dot -Tjson to get positions in JSON format
        """

        # Generate DOT file content
        dot_content = "digraph G {\n"
        dot_content += "  rankdir=TB;\n"
        dot_content += "  nodesep=1.5;\n"
        dot_content += "  ranksep=2.0;\n"

        # Add nodes
        for node_id, node_data in G.nodes(data=True):
            width = node_data.get('width', 1.5)
            height = node_data.get('height', 1.5)
            dot_content += f'  "{node_id}" [width={width}, height={height}];\n'

        # Add edges
        for source, target in G.edges():
            dot_content += f'  "{source}" -> "{target}";\n'

        dot_content += "}\n"

        logger.debug(f"Generated DOT:\n{dot_content}")

        # Write to temp file and run dot
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as f:
            f.write(dot_content)
            dot_file = f.name

        try:
            # Run dot -Tjson to get layout in JSON format
            result = subprocess.run(
                ['dot', '-Tjson', dot_file],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            # Parse JSON output
            layout_json = json.loads(result.stdout)

            # Extract node positions from JSON
            pos = {}
            for obj in layout_json.get('objects', []):
                if obj.get('_gvid') is not None:
                    node_id = obj.get('name')
                    # Graphviz returns positions in points (72 points = 1 inch)
                    # Get center position
                    pos_str = obj.get('pos', '0,0')
                    x_str, y_str = pos_str.split(',')
                    x = float(x_str)
                    y = float(y_str)
                    pos[node_id] = (x, y)

            logger.info(f"Parsed {len(pos)} positions from Graphviz JSON")
            return pos

        except subprocess.CalledProcessError as e:
            logger.error(f"Graphviz dot command failed: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Graphviz JSON output: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error running Graphviz: {e}")
            raise

    def _apply_rte_constraints(
        self,
        nodes: List[Dict],
        pos: Dict[str, Tuple[float, float]],
        G: nx.DiGraph
    ) -> Dict[str, Tuple[float, float]]:
        """
        Apply RTE rules to Graphviz positions

        Rules:
        - Busbars must be horizontal (same Y for all busbars)
        - Equipment in same bay must be vertically aligned (same X)
        - Equipment positioned below their connected busbar
        - Proper spacing between bays
        """

        pos_adjusted = {}

        # Group nodes by type and bay
        busbars = []
        equipment_by_bay = {}
        busbar_to_equipment = {}  # Track which equipment connects to each busbar

        for node in nodes:
            node_id = node['id']
            node_type = node.get('type')
            node_data = node.get('data', {})

            if node_type == 'busbar':
                busbars.append(node_id)
                busbar_to_equipment[node_id] = []
            elif node_type == 'equipment':
                bay_name = node_data.get('bayName', 'unknown')
                if bay_name not in equipment_by_bay:
                    equipment_by_bay[bay_name] = []
                equipment_by_bay[bay_name].append(node_id)

        # Build busbar-to-equipment mapping from edges
        for source, target in G.edges():
            if source in busbar_to_equipment:
                busbar_to_equipment[source].append(target)

        logger.info(f"RTE Layout: {len(busbars)} busbars, {len(equipment_by_bay)} bays")

        # 1. Position busbars horizontally at top
        busbar_y = 50  # Fixed Y position for all busbars (horizontal line)

        for busbar_id in busbars:
            # Busbars span horizontally at top
            pos_adjusted[busbar_id] = (100, busbar_y)
            logger.debug(f"Busbar {busbar_id} positioned at (100, {busbar_y})")

        # 2. Position equipment vertically in bays below busbars
        bay_names_sorted = sorted(equipment_by_bay.keys())

        for bay_index, bay_name in enumerate(bay_names_sorted):
            equipment_ids = equipment_by_bay[bay_name]

            # Calculate X position for this bay
            bay_x = 200 + bay_index * self.rte_rules['bay_horizontal_spacing']

            # Position each equipment vertically below busbar
            for eq_index, eq_id in enumerate(equipment_ids):
                # Position below busbar with vertical spacing
                eq_y = busbar_y + 150 + eq_index * self.rte_rules['equipment_vertical_spacing']
                pos_adjusted[eq_id] = (bay_x, eq_y)

                if eq_index == 0:
                    logger.debug(f"Bay {bay_name}: X={bay_x}, equipment count={len(equipment_ids)}")

        return pos_adjusted

    def _fallback_grid_layout(self, nodes: List[Dict]) -> Dict[str, Tuple[float, float]]:
        """
        Simple grid layout as fallback if Graphviz fails
        """
        logger.warning("Using fallback grid layout")

        pos = {}
        grid_size = 10

        for i, node in enumerate(nodes):
            row = i // grid_size
            col = i % grid_size
            pos[node['id']] = (col * 150, row * 150)

        return pos


def calculate_layout_with_graphviz(
    nodes: List[Dict],
    edges: List[Dict]
) -> Tuple[List[Dict], List[Dict]]:
    """
    Helper function to calculate layout with Graphviz

    Args:
        nodes: ReactFlow nodes (without positions)
        edges: ReactFlow edges

    Returns:
        (nodes_with_positions, edges)
    """
    engine = GraphvizLayoutEngine()
    return engine.calculate_layout(nodes, edges)
