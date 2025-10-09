"""
RTE Single Line Diagram Representation Rules
Convention de représentation des schémas unifilaires selon les règles RTE France
"""

from typing import Dict, List, Literal
from dataclasses import dataclass
from enum import Enum


class EquipmentOrientation(Enum):
    """Orientation des équipements"""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class BayDirection(Enum):
    """Direction des départs"""
    UP = "up"      # Vers le haut (buissage, alimentation)
    DOWN = "down"  # Vers le bas (lignes, transformateurs)
    LEFT = "left"  # Vers la gauche (couplage)
    RIGHT = "right"  # Vers la droite (couplage)


@dataclass
class RTELayoutRules:
    """
    Règles de layout pour les schémas unifilaires RTE

    Conventions RTE :
    - Jeux de barres toujours horizontaux
    - Pas de départ 1/2 disjoncteur (un départ = un seul JdB)
    - JdB multiples empilés verticalement
    - Couplage de barres (CBO) sur le côté
    - Gestion des sections/omnibus sur un même JdB
    """

    # Espacement
    busbar_vertical_spacing: int = 200  # Espacement vertical entre JdB
    bay_horizontal_spacing: int = 150   # Espacement horizontal entre départs
    equipment_vertical_spacing: int = 80  # Espacement vertical entre équipements

    # Jeux de barres
    busbar_orientation: EquipmentOrientation = EquipmentOrientation.HORIZONTAL
    busbar_order: List[str] = None  # Ordre des JdB (ex: ["101", "102", "103"])
    busbar_height: int = 10  # Épaisseur visuelle du JdB

    # Départs
    allow_half_breaker_bays: bool = False  # RTE : toujours False
    bay_attachment_mode: Literal["single", "double"] = "single"  # RTE : "single"

    # Couplage de barres (CBO)
    coupling_position: Literal["left", "right", "both"] = "left"
    coupling_width: int = 100  # Largeur réservée pour le CBO

    # Sections de barres
    busbar_sections_enabled: bool = True  # Support des sections/omnibus
    section_separator_width: int = 30  # Largeur du séparateur entre sections

    # Ordres de layers (couches verticales pour les équipements)
    equipment_layers: Dict[str, int] = None

    def __post_init__(self):
        """Initialisation des valeurs par défaut"""
        if self.busbar_order is None:
            # Ordre standard RTE : JdB du plus haut voltage au plus bas
            self.busbar_order = ["101", "102", "103"]

        if self.equipment_layers is None:
            # Ordre vertical standard RTE pour un départ
            self.equipment_layers = {
                "BUSBAR": 0,      # Jeu de barres
                "DIS_SA": 1,      # Sectionneur d'aiguillage (haut)
                "DIS_SL": 2,      # Sectionneur de ligne
                "CBR": 3,         # Disjoncteur
                "DIS_ST": 4,      # Sectionneur de terre
                "CTR": 5,         # Transformateur de courant
                "VTR": 5,         # Transformateur de tension (même niveau que TC)
                "TERMINAL": 6     # Point de départ (ligne/transfo)
            }


@dataclass
class BusbarSection:
    """
    Section d'un jeu de barres

    Un JdB peut être divisé en plusieurs sections (omnibus, sectionnement)
    Exemple : JdB 101 section A et section B
    """
    node: str  # Ex: "101"
    section_id: str  # Ex: "A", "B", ou "" si pas de section
    connectivity_node: str  # ConnectivityNode RDF
    x_start: int = 0
    x_end: int = 0
    bays: List[str] = None  # Liste des Bays connectés à cette section

    def __post_init__(self):
        if self.bays is None:
            self.bays = []


@dataclass
class CouplingBay:
    """
    Travée de couplage de barres (CBO)

    Connecte deux jeux de barres (ou deux sections)
    Position : côté gauche ou droit du schéma
    """
    name: str
    from_busbar: str  # Ex: "101"
    to_busbar: str    # Ex: "102"
    position: Literal["left", "right"]
    equipment: List[str] = None  # Liste des équipements (DJ, SA, etc.)

    def __post_init__(self):
        if self.equipment is None:
            self.equipment = []


@dataclass
class RTEEquipmentSymbol:
    """
    Symbole d'un équipement selon les conventions RTE
    """
    type: str  # CBR, DIS, CTR, VTR, etc.
    subtype: str = ""  # SA, SL, ST, SS pour les sectionneurs
    width: int = 40
    height: int = 60
    terminals: List[Dict] = None  # Points de connexion
    svg_template: str = ""  # Template SVG du symbole

    def __post_init__(self):
        if self.terminals is None:
            # Par défaut : 2 terminaux (haut et bas)
            self.terminals = [
                {"id": "top", "x": 20, "y": 0},
                {"id": "bottom", "x": 20, "y": 60}
            ]


class RTERenderingNamespace:
    """
    Namespace de rendu RTE

    Contient toutes les règles et configurations pour générer
    un schéma unifilaire selon les conventions RTE
    """

    def __init__(self):
        self.rules = RTELayoutRules()
        self.symbols: Dict[str, RTEEquipmentSymbol] = {}
        self._init_symbols()

    def _init_symbols(self):
        """Initialise la bibliothèque de symboles RTE"""
        # Ces symboles seront définis en SVG
        self.symbols = {
            "CBR": RTEEquipmentSymbol(
                type="CBR",
                width=40,
                height=60,
                svg_template="circuit_breaker"
            ),
            "DIS_SA": RTEEquipmentSymbol(
                type="DIS",
                subtype="SA",
                width=40,
                height=50,
                svg_template="disconnector_sa"
            ),
            "DIS_SL": RTEEquipmentSymbol(
                type="DIS",
                subtype="SL",
                width=40,
                height=50,
                svg_template="disconnector_sl"
            ),
            "DIS_ST": RTEEquipmentSymbol(
                type="DIS",
                subtype="ST",
                width=40,
                height=50,
                svg_template="disconnector_st"
            ),
            "DIS_SS": RTEEquipmentSymbol(
                type="DIS",
                subtype="SS",
                width=40,
                height=50,
                svg_template="disconnector_ss"
            ),
            "CTR": RTEEquipmentSymbol(
                type="CTR",
                width=40,
                height=50,
                svg_template="current_transformer"
            ),
            "VTR": RTEEquipmentSymbol(
                type="VTR",
                width=40,
                height=50,
                svg_template="voltage_transformer"
            ),
            "PTR": RTEEquipmentSymbol(
                type="PTR",
                width=60,
                height=80,
                svg_template="power_transformer",
                terminals=[
                    {"id": "primary", "x": 30, "y": 0},
                    {"id": "secondary1", "x": 15, "y": 80},
                    {"id": "secondary2", "x": 45, "y": 80}
                ]
            )
        }

    def get_equipment_layer(self, equipment_type: str, equipment_subtype: str = "") -> int:
        """
        Retourne la couche (layer) verticale pour un équipement

        Args:
            equipment_type: Type d'équipement (CBR, DIS, CTR, etc.)
            equipment_subtype: Sous-type (SA, SL, ST, SS pour sectionneurs)

        Returns:
            Numéro de couche (0 = jeu de barres, croissant vers le bas)
        """
        if equipment_type == "DIS" and equipment_subtype:
            key = f"{equipment_type}_{equipment_subtype}"
        else:
            key = equipment_type

        return self.rules.equipment_layers.get(key, 999)  # 999 = non défini

    def get_busbar_y_position(self, node: str) -> int:
        """
        Retourne la position Y d'un jeu de barres

        Args:
            node: Numéro du JdB (ex: "101", "102", "103")

        Returns:
            Position Y en pixels
        """
        try:
            index = self.rules.busbar_order.index(node)
            return index * self.rules.busbar_vertical_spacing
        except ValueError:
            # JdB non trouvé, mettre à la fin
            return len(self.rules.busbar_order) * self.rules.busbar_vertical_spacing

    def should_render_coupling_left(self) -> bool:
        """Indique si le couplage doit être rendu à gauche"""
        return self.rules.coupling_position in ["left", "both"]

    def should_render_coupling_right(self) -> bool:
        """Indique si le couplage doit être rendu à droite"""
        return self.rules.coupling_position in ["right", "both"]


# Instance globale des règles RTE
RTE_NAMESPACE = RTERenderingNamespace()
