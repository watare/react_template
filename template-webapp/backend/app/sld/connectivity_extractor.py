"""
ConnectivityNode Extractor

Extracts connectivity topology from IEC 61850 RDF:
- Equipment → Terminal → ConnectivityNode
- Groups equipment by ConnectivityNode to create edges
- Validates connections (must have 2+ equipment per CN)

This is Step 1 of the diagram generation pipeline.
"""

import logging
from typing import Dict, List, Tuple, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectivityTopology:
    """
    Represents the connectivity topology extracted from IEC 61850 RDF

    Structure:
    - equipment_nodes: Dict[equipment_id, equipment_data]
    - connectivity_map: Dict[cn_name, List[equipment_id]]
    - edges: List[Tuple[equipment_id1, equipment_id2, cn_name]]
    """

    def __init__(self):
        self.equipment_nodes: Dict[str, Dict] = {}
        self.connectivity_map: Dict[str, List[Dict]] = defaultdict(list)
        self.edges: List[Tuple[str, str, str]] = []
        self.busbars: Dict[str, Dict] = {}

    def add_equipment(
        self,
        equipment_name: str,
        equipment_type: str,
        bay_name: str,
        voltage_level_name: str,
        substation_name: str,
        equipment_subtype: str = None,
        order: int = 999
    ):
        """
        Add equipment node to topology

        Args:
            equipment_name: Equipment identifier
            equipment_type: CBR, DIS, CTR, VTR, PTR, etc.
            bay_name: Bay name
            voltage_level_name: Voltage level
            substation_name: Substation
            equipment_subtype: Optional subtype (SA, SL, ST, SS)
            order: Display order
        """
        if equipment_name not in self.equipment_nodes:
            self.equipment_nodes[equipment_name] = {
                "name": equipment_name,
                "type": equipment_type,
                "subtype": equipment_subtype,
                "bay_name": bay_name,
                "voltage_level_name": voltage_level_name,
                "substation_name": substation_name,
                "order": order,
                "terminals": []
            }

    def add_terminal_connection(
        self,
        equipment_name: str,
        terminal_name: str,
        cn_name: str
    ):
        """
        Add terminal connection to equipment

        Args:
            equipment_name: Equipment identifier
            terminal_name: Terminal identifier
            cn_name: ConnectivityNode name
        """
        if equipment_name in self.equipment_nodes:
            self.equipment_nodes[equipment_name]["terminals"].append({
                "terminal_name": terminal_name,
                "cn_name": cn_name
            })

            # Track connectivity mapping
            self.connectivity_map[cn_name].append({
                "equipment": equipment_name,
                "terminal": terminal_name
            })

    def add_busbar(
        self,
        busbar_id: str,
        voltage_level_name: str,
        voltage: str = None
    ):
        """
        Add busbar node

        Args:
            busbar_id: Busbar identifier
            voltage_level_name: Voltage level
            voltage: Optional voltage value
        """
        self.busbars[busbar_id] = {
            "id": busbar_id,
            "voltage_level_name": voltage_level_name,
            "voltage": voltage
        }

    def build_edges(self):
        """
        Build edges from connectivity map

        Strategy:
        1. Check if explicit BUSBAR equipment exists → use their ConnectivityNodes
        2. Otherwise, infer busbars from SA disconnectors (SA1 → BB1, SA2 → BB2)
        3. Create equipment-to-equipment edges for regular ConnectivityNodes
        """
        self.edges = []

        # Step 1: Identify BUSBAR equipment (if any)
        busbar_equipment = {
            eq_uri: eq_data for eq_uri, eq_data in self.equipment_nodes.items()
            if eq_data.get("type") == "BUSBAR"
        }

        logger.info(f"Found {len(busbar_equipment)} explicit BUSBAR equipment")

        if busbar_equipment:
            # Case 1: Explicit BUSBARs exist
            self._build_edges_with_explicit_busbars(busbar_equipment)
        else:
            # Case 2: No explicit BUSBARs - infer from SA disconnectors
            logger.info("No explicit BUSBAR found, inferring from SA disconnectors")
            self._build_edges_with_inferred_busbars()

        # Step 2: Create equipment-to-equipment edges for non-busbar ConnectivityNodes
        for cn_name, terminals in self.connectivity_map.items():
            if len(terminals) < 2:
                continue

            equipment_list = [t["equipment"] for t in terminals]
            unique_equipment = list(set(equipment_list))

            # Skip if this CN already handled by busbar logic
            is_busbar_cn = any(
                cn_name in eq_data.get("terminals", [{}])[0].get("cn_name", "")
                for eq_data in self.busbars.values()
            )
            if is_busbar_cn:
                continue

            # Create mesh edges between equipment sharing this CN
            if len(unique_equipment) >= 2:
                for i in range(len(unique_equipment) - 1):
                    for j in range(i + 1, len(unique_equipment)):
                        eq1 = unique_equipment[i]
                        eq2 = unique_equipment[j]
                        self.edges.append((eq1, eq2, cn_name))
                        logger.debug(f"Equipment edge: {eq1} <-[{cn_name}]-> {eq2}")

        logger.info(f"Built {len(self.edges)} edges from {len(self.connectivity_map)} ConnectivityNodes")

    def _build_edges_with_explicit_busbars(self, busbar_equipment: Dict):
        """
        Build edges when explicit BUSBAR equipment exists

        For each BUSBAR:
        - Extract its ConnectivityNodes (from terminals)
        - Find all other equipment connected to same CNs
        - Create busbar → equipment edges
        """
        for busbar_uri, busbar_data in busbar_equipment.items():
            busbar_name = busbar_data.get("display_name", busbar_uri)
            terminals = busbar_data.get("terminals", [])

            logger.info(f"Processing BUSBAR: {busbar_name} with {len(terminals)} terminals")

            # Get all ConnectivityNodes connected to this busbar
            busbar_cns = [t["cn_name"] for t in terminals]

            # Add this busbar to busbars dict
            if busbar_uri not in self.busbars:
                self.busbars[busbar_uri] = {
                    "id": busbar_uri,
                    "voltage_level_name": busbar_data.get("voltage_level_name", "unknown"),
                    "voltage": None,
                    "cn_names": busbar_cns
                }

            # Find all equipment connected to these CNs
            for cn_name in busbar_cns:
                if cn_name not in self.connectivity_map:
                    continue

                terminals_on_cn = self.connectivity_map[cn_name]
                for terminal_info in terminals_on_cn:
                    eq_uri = terminal_info["equipment"]

                    # Don't create edge to itself
                    if eq_uri == busbar_uri:
                        continue

                    # Create edge: busbar → equipment
                    self.edges.append((busbar_uri, eq_uri, cn_name))
                    logger.debug(f"BUSBAR edge: {busbar_name} -[{cn_name}]-> {eq_uri}")

    def _build_edges_with_inferred_busbars(self):
        """
        Infer busbars from SA disconnectors when no explicit BUSBAR equipment

        Logic:
        - Only SA1 found → 1 busbar (BB1) - simple barre
        - SA1 + SA2 found → 2 busbars (BB1, BB2) - double jeu de barres
        - SA1 + SA2 + SA3 found → 3 busbars (rare)

        Important: Create ONE busbar per UNIQUE SA number, not per SA equipment
        """
        # Group SA disconnectors by voltage level and number
        sa_by_voltage_level = {}  # {voltage_level: {1: [SA1 equipment URIs], 2: [SA2 equipment URIs]}}

        for eq_uri, eq_data in self.equipment_nodes.items():
            eq_type = eq_data.get("type")
            eq_subtype = eq_data.get("subtype")
            voltage_level = eq_data.get("voltage_level_name")

            # Check if this is an SA disconnector
            if eq_type == "DIS" and eq_subtype and eq_subtype.startswith("SA"):
                # Extract SA number (SA1 → 1, SA2 → 2)
                try:
                    sa_number = int(eq_subtype[2:])  # "SA1" → 1
                except (ValueError, IndexError):
                    continue

                if voltage_level not in sa_by_voltage_level:
                    sa_by_voltage_level[voltage_level] = {}

                if sa_number not in sa_by_voltage_level[voltage_level]:
                    sa_by_voltage_level[voltage_level][sa_number] = []

                sa_by_voltage_level[voltage_level][sa_number].append(eq_uri)

        logger.info(f"Found SA disconnectors in {len(sa_by_voltage_level)} voltage levels")

        # Create ONE virtual busbar per UNIQUE SA number in each voltage level
        for voltage_level, sa_groups in sa_by_voltage_level.items():
            busbar_numbers = sorted(sa_groups.keys())
            logger.info(f"Voltage level {voltage_level}: detected SA{busbar_numbers} → creating {len(busbar_numbers)} busbar(s)")

            for bb_number in busbar_numbers:
                sa_equipment_list = sa_groups[bb_number]

                # Create ONE virtual busbar node for this SA number
                busbar_id = f"busbar_BB{bb_number}_{voltage_level}"

                self.busbars[busbar_id] = {
                    "id": busbar_id,
                    "voltage_level_name": voltage_level,
                    "voltage": None,
                    "busbar_number": bb_number,
                    "inferred": True,  # Mark as inferred (not explicit equipment)
                    "sa_count": len(sa_equipment_list)  # How many SA equipment connect to this busbar
                }
                logger.info(f"Created virtual busbar: {busbar_id} (from {len(sa_equipment_list)} SA{bb_number} equipment)")

                # Collect all ConnectivityNodes from all SA equipment with this number
                busbar_cn_set = set()
                for sa_uri in sa_equipment_list:
                    sa_data = self.equipment_nodes[sa_uri]
                    sa_terminals = sa_data.get("terminals", [])
                    for terminal in sa_terminals:
                        busbar_cn_set.add(terminal["cn_name"])

                logger.debug(f"Busbar {busbar_id} covers {len(busbar_cn_set)} ConnectivityNodes")

                # Connect busbar to ALL equipment on these ConnectivityNodes
                for cn_name in busbar_cn_set:
                    if cn_name not in self.connectivity_map:
                        continue

                    terminals_on_cn = self.connectivity_map[cn_name]
                    for terminal_info in terminals_on_cn:
                        eq_uri = terminal_info["equipment"]

                        # Create edge: busbar → equipment (including SA themselves)
                        self.edges.append((busbar_id, eq_uri, cn_name))
                        logger.debug(f"Virtual busbar edge: {busbar_id} -[{cn_name}]-> {eq_uri}")

    def _is_busbar_connectivity_node(self, cn_name: str) -> bool:
        """
        Check if a ConnectivityNode name represents a Busbar (JDB)

        RTE convention: Busbar CN names contain BUIS, BB, JDB in Bay name
        Exclude: CBO (couplage), TR (transformateur)

        Examples:
        - "POSTE/4/4BUIS1/..." → True (busbar)
        - "POSTE/4/4BUIS2/..." → True (busbar)
        - "POSTE/4/4CBO1/..." → False (couplage)
        - "POSTE/4/4TR412/..." → False (transformateur)
        """
        # Extract Bay name from CN path (format: POSTE/X/BAYNAME/...)
        parts = cn_name.split('/')
        if len(parts) < 3:
            return False

        bay_name = parts[2].upper()

        # Exclude non-busbar patterns first
        if "CBO" in bay_name or "COUPL" in bay_name:
            return False  # Couplage, not a busbar
        if "TR" in bay_name and ("4TR" in bay_name or "3TR" in bay_name or "2TR" in bay_name):
            return False  # Transformateur, not a busbar

        # Check for busbar patterns in Bay name
        return "BUIS" in bay_name or "BB" in bay_name or "JDB" in bay_name

    def _find_busbar_for_cn(self, cn_name: str) -> str:
        """
        Return busbar node ID for this ConnectivityNode

        Extract Bay name from CN path and use as busbar ID
        Example: "POSTE/4/4BUIS1/_uuid-1" → "busbar_4BUIS1"
        """
        # Extract Bay name from CN path (format: POSTE/X/BAYNAME/...)
        parts = cn_name.split('/')
        if len(parts) >= 3:
            bay_name = parts[2]  # Extract "4BUIS1", "4BUIS2", etc.
            return f"busbar_{bay_name}"

        # Fallback: use full CN name
        return f"busbar_{cn_name}"

    def _extract_voltage_level_from_equipment(self, equipment_uris: list) -> str:
        """
        Extract voltage level from equipment connected to this busbar
        """
        if not equipment_uris:
            return "unknown"

        # Get voltage level from first equipment
        first_eq_uri = equipment_uris[0]
        if first_eq_uri in self.equipment_nodes:
            return self.equipment_nodes[first_eq_uri].get("voltage_level_name", "unknown")

        return "unknown"

    def get_statistics(self) -> Dict:
        """
        Get topology statistics

        Returns:
            Statistics dictionary
        """
        cns_with_connections = sum(1 for terminals in self.connectivity_map.values() if len(terminals) >= 2)

        return {
            "equipment_count": len(self.equipment_nodes),
            "busbar_count": len(self.busbars),
            "connectivity_nodes": len(self.connectivity_map),
            "connectivity_nodes_with_connections": cns_with_connections,
            "edge_count": len(self.edges),
            "terminals_total": sum(len(eq["terminals"]) for eq in self.equipment_nodes.values())
        }

    def validate(self) -> List[str]:
        """
        Validate topology and return warnings

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check for equipment without terminals
        equipment_without_terminals = [
            eq_name for eq_name, eq_data in self.equipment_nodes.items()
            if len(eq_data["terminals"]) == 0
        ]

        if equipment_without_terminals:
            warnings.append(
                f"Found {len(equipment_without_terminals)} equipment without terminals: "
                f"{', '.join(equipment_without_terminals[:5])}"
            )

        # Check for isolated equipment (no edges)
        equipment_in_edges = set()
        for eq1, eq2, _ in self.edges:
            equipment_in_edges.add(eq1)
            equipment_in_edges.add(eq2)

        isolated_equipment = [
            eq_name for eq_name in self.equipment_nodes.keys()
            if eq_name not in equipment_in_edges
        ]

        if isolated_equipment:
            warnings.append(
                f"Found {len(isolated_equipment)} isolated equipment (no connections): "
                f"{', '.join(isolated_equipment[:5])}"
            )

        # Check for ConnectivityNodes with only 1 terminal
        single_terminal_cns = [
            cn_name for cn_name, terminals in self.connectivity_map.items()
            if len(terminals) == 1
        ]

        if single_terminal_cns:
            warnings.append(
                f"Found {len(single_terminal_cns)} ConnectivityNodes with only 1 terminal "
                f"(may indicate incomplete topology)"
            )

        return warnings


def extract_connectivity_from_sparql_results(results: List[Dict]) -> ConnectivityTopology:
    """
    Extract connectivity topology from SPARQL query results

    Args:
        results: SPARQL results (bindings JSON from Fuseki)

    Returns:
        ConnectivityTopology object
    """
    topology = ConnectivityTopology()

    logger.info(f"Extracting connectivity from {len(results)} SPARQL rows")

    rows_with_equipment = 0
    rows_with_terminals = 0
    rows_skipped_hierarchy = 0

    for binding in results:
        # Extract values
        substation_name = binding.get("substationName", {}).get("value")
        vl_name = binding.get("voltageLevelName", {}).get("value")
        bay_name = binding.get("bayName", {}).get("value")
        equipment_uri = binding.get("equipment", {}).get("value")
        equipment_name = binding.get("equipmentName", {}).get("value")

        if not all([substation_name, vl_name, bay_name]):
            rows_skipped_hierarchy += 1
            continue

        # Add equipment node (use URI as unique ID, name as label)
        if equipment_uri and equipment_name:
            rows_with_equipment += 1

            equipment_type = binding.get("equipmentType", {}).get("value")
            equipment_subtype = binding.get("equipmentSubtype", {}).get("value")
            order_value = binding.get("equipmentOrder", {}).get("value")

            try:
                order = int(order_value) if order_value else 999
            except (ValueError, TypeError):
                order = 999

            topology.add_equipment(
                equipment_name=equipment_uri,  # Use URI as unique key
                equipment_type=equipment_type,
                bay_name=bay_name,
                voltage_level_name=vl_name,
                substation_name=substation_name,
                equipment_subtype=equipment_subtype,
                order=order
            )
            # Store the display name separately
            topology.equipment_nodes[equipment_uri]["display_name"] = equipment_name

            # Add terminal connection
            terminal_name = binding.get("terminalName", {}).get("value")
            cn_name = binding.get("terminalCNodeName", {}).get("value")

            if terminal_name and cn_name:
                rows_with_terminals += 1
                topology.add_terminal_connection(
                    equipment_name=equipment_uri,  # Use URI
                    terminal_name=terminal_name,
                    cn_name=cn_name
                )

    logger.info(f"Extracted: {rows_with_equipment} equipment rows, {rows_with_terminals} with terminals, skipped {rows_skipped_hierarchy} rows (missing hierarchy)")

    # Log ConnectivityNode names to identify busbars
    cn_names = list(topology.connectivity_map.keys())
    logger.info(f"DEBUG: ConnectivityNode names: {cn_names[:10]}")  # First 10

    # Build edges from connectivity map
    topology.build_edges()

    # Validate topology
    warnings = topology.validate()
    for warning in warnings:
        logger.warning(f"Topology validation: {warning}")

    # Log statistics
    stats = topology.get_statistics()
    logger.info(f"Connectivity topology: {stats}")

    return topology
