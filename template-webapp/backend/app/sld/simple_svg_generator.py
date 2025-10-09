"""
Générateur SVG simple pour SLD (POC)

Ce générateur crée un schéma unifilaire basique en SVG sans PowSyBl.
But : Tester rapidement que les requêtes SPARQL extraient bien les bonnes données.

Layout simple :
- Jeux de barres horizontaux (un par VoltageLevel)
- Équipements en colonnes verticales (un par Bay)
- Rectangles + texte pour représenter les équipements
- Lignes pour la connectivité
"""

from typing import List, Dict, Tuple
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class SimpleSVGGenerator:
    """
    Générateur SVG minimaliste pour visualiser rapidement la topologie

    Conventions de layout :
    - 1 ligne horizontale = 1 VoltageLevel (jeu de barres)
    - 1 colonne verticale = 1 Bay (travée)
    - Espacement fixe entre éléments
    """

    # Dimensions et espacements (en pixels) - depuis config
    BUSBAR_HEIGHT = settings.SLD_BUSBAR_HEIGHT
    BAY_WIDTH = settings.SLD_BAY_WIDTH
    EQUIPMENT_HEIGHT = settings.SLD_EQUIPMENT_HEIGHT
    EQUIPMENT_WIDTH = settings.SLD_EQUIPMENT_WIDTH
    VERTICAL_SPACING = settings.SLD_VERTICAL_SPACING
    HORIZONTAL_SPACING = settings.SLD_HORIZONTAL_SPACING
    MARGIN = settings.SLD_MARGIN

    # Ordre d'affichage des équipements depuis le jeu de barres (conventions RTE)
    # Plus le numéro est petit, plus l'équipement est proche du busbar
    EQUIPMENT_ORDER = {
        "DIS": 1,   # Sectionneurs en premier (SA, SL, ST, SS)
        "CBR": 2,   # Disjoncteur après les sectionneurs
        "CTR": 3,   # Transformateur de courant
        "VTR": 4,   # Transformateur de tension
        "PTR": 5,   # Transformateur de puissance
        "CAP": 6,   # Condensateur
        "REA": 7,   # Réactance
        "GEN": 8,   # Générateur
        "BAT": 9,   # Batterie
        "MOT": 10   # Moteur
    }

    # Couleurs par type d'équipement - depuis config
    @property
    def EQUIPMENT_COLORS(self):
        return {
            "CBR": f"#{settings.SLD_COLOR_CBR}",
            "DIS": f"#{settings.SLD_COLOR_DIS}",
            "CTR": f"#{settings.SLD_COLOR_CTR}",
            "VTR": f"#{settings.SLD_COLOR_VTR}",
            "PTR": f"#{settings.SLD_COLOR_PTR}",
            "CAP": f"#{settings.SLD_COLOR_CAP}",
            "REA": f"#{settings.SLD_COLOR_REA}",
            "GEN": f"#{settings.SLD_COLOR_GEN}",
            "BAT": f"#{settings.SLD_COLOR_BAT}",
            "DEFAULT": f"#{settings.SLD_COLOR_DEFAULT}"
        }

    def __init__(self):
        self.width = 1200
        self.height = 800
        self.svg_elements = []

    def generate(self, topology_data: Dict) -> str:
        """
        Génère un SVG à partir des données de topologie

        Args:
            topology_data: Dictionnaire contenant :
                - substations: Liste des substations
                - voltage_levels: Liste des niveaux de tension
                - bays: Liste des travées
                - equipments: Liste des équipements
                - connectivity: Liste des connexions

        Returns:
            String SVG
        """
        logger.info("Generating simple SVG diagram")

        # Réinitialiser
        self.svg_elements = []

        # Organiser les données
        organized = self._organize_data(topology_data)

        # Calculer les dimensions nécessaires
        self._calculate_dimensions(organized)

        # Générer les éléments SVG
        self._draw_substations(organized)
        self._draw_voltage_levels(organized)
        self._draw_bays(organized)
        self._draw_equipment(organized)
        self._draw_connectivity(organized)

        # Assembler le SVG
        svg = self._build_svg()

        logger.info(f"SVG generated: {self.width}x{self.height}px")
        return svg

    def _organize_data(self, topology_data: Dict) -> Dict:
        """
        Organise les données en structure hiérarchique pour le layout

        Structure :
        {
            "SUBSTATION_NAME": {
                "voltage_levels": {
                    "VL_NAME": {
                        "voltage": 225000,
                        "y_position": 200,
                        "bays": {
                            "BAY_NAME": {
                                "x_position": 300,
                                "equipments": [...],
                                "is_coupling": False
                            }
                        }
                    }
                }
            }
        }
        """
        organized = {}

        # Grouper par Substation → VoltageLevel → Bay
        for bay in topology_data.get("bays", []):
            substation_name = bay["substationName"]
            vl_name = bay["voltageLevelName"]
            bay_name = bay["bayName"]

            # Initialiser la structure si nécessaire
            if substation_name not in organized:
                organized[substation_name] = {"voltage_levels": {}}

            if vl_name not in organized[substation_name]["voltage_levels"]:
                organized[substation_name]["voltage_levels"][vl_name] = {
                    "voltage": bay.get("voltage", "Unknown"),
                    "bays": {}
                }

            if bay_name not in organized[substation_name]["voltage_levels"][vl_name]["bays"]:
                # Détecter si c'est un couplage de barres
                is_coupling = ("CBO" in bay_name.upper() or
                             "COUPL" in bay_name.upper() or
                             "COUPLING" in bay_name.upper())

                organized[substation_name]["voltage_levels"][vl_name]["bays"][bay_name] = {
                    "equipments": [],
                    "is_coupling": is_coupling
                }

        # Ajouter les équipements dans les bays
        for equipment in topology_data.get("equipments", []):
            substation_name = equipment["substationName"]
            vl_name = equipment["voltageLevelName"]
            bay_name = equipment["bayName"]

            if (substation_name in organized and
                vl_name in organized[substation_name]["voltage_levels"] and
                bay_name in organized[substation_name]["voltage_levels"][vl_name]["bays"]):

                organized[substation_name]["voltage_levels"][vl_name]["bays"][bay_name]["equipments"].append({
                    "name": equipment["equipmentName"],
                    "type": equipment["equipmentType"],
                    "subtype": equipment.get("equipmentSubtype"),
                    "order": equipment.get("equipmentOrder", 999)
                })

        # Trier les équipements dans chaque bay selon l'ordre du fichier SCD
        for substation in organized.values():
            for vl_data in substation["voltage_levels"].values():
                for bay_data in vl_data["bays"].values():
                    bay_data["equipments"].sort(key=lambda eq: (
                        eq.get("order", 999),  # Utiliser l'ordre du fichier SCD
                        self.EQUIPMENT_ORDER.get(eq["type"], 999),  # Fallback: ordre par type
                        eq["name"]  # Fallback final: nom alphabétique
                    ))

        return organized

    def _calculate_dimensions(self, organized: Dict):
        """Calcule les dimensions du SVG en fonction du nombre d'éléments"""
        max_bays = 0
        num_voltage_levels = 0

        for substation in organized.values():
            for vl in substation["voltage_levels"].values():
                # Compter seulement les bays non vides
                non_empty_bays = sum(1 for bay in vl["bays"].values() if len(bay["equipments"]) > 0)
                if non_empty_bays > 0:
                    num_voltage_levels += 1
                    max_bays = max(max_bays, non_empty_bays)

        self.width = self.MARGIN * 2 + max_bays * (self.BAY_WIDTH + self.HORIZONTAL_SPACING)
        self.height = self.MARGIN * 2 + num_voltage_levels * (self.BUSBAR_HEIGHT + self.VERTICAL_SPACING * 5)

    def _draw_substations(self, organized: Dict):
        """Dessine les cadres des substations"""
        for substation_name in organized.keys():
            self.svg_elements.append(f'''
                <text x="{self.MARGIN}" y="{self.MARGIN - 10}"
                      font-size="20" font-weight="bold" fill="#333">
                    {substation_name}
                </text>
            ''')

    def _draw_voltage_levels(self, organized: Dict):
        """Dessine les jeux de barres (lignes horizontales)"""
        y = self.MARGIN + self.BUSBAR_HEIGHT

        for substation in organized.values():
            for vl_name, vl_data in substation["voltage_levels"].items():
                # Skip voltage levels with only empty bays
                non_empty_bays = sum(1 for bay in vl_data["bays"].values() if len(bay["equipments"]) > 0)
                if non_empty_bays == 0:
                    continue

                # Stocker la position Y pour ce voltage level
                vl_data["y_position"] = y

                # Ligne horizontale pour le jeu de barres
                x_end = self.width - self.MARGIN
                self.svg_elements.append(f'''
                    <line x1="{self.MARGIN}" y1="{y}"
                          x2="{x_end}" y2="{y}"
                          stroke="#333" stroke-width="4"/>
                ''')

                # Label du voltage level
                voltage_display = f"{vl_name}"
                if vl_data.get("voltage"):
                    voltage_display += f" ({vl_data['voltage']}V)"

                self.svg_elements.append(f'''
                    <text x="{self.MARGIN + 10}" y="{y - 10}"
                          font-size="14" font-weight="bold" fill="#333">
                        {voltage_display}
                    </text>
                ''')

                y += self.BUSBAR_HEIGHT + self.VERTICAL_SPACING * 5

    def _draw_bays(self, organized: Dict):
        """Dessine les travées (colonnes verticales)"""
        for substation in organized.values():
            for vl_data in substation["voltage_levels"].values():
                # Skip if no y_position (means voltage level was skipped)
                if "y_position" not in vl_data:
                    continue

                x = self.MARGIN + self.HORIZONTAL_SPACING

                for bay_name, bay_data in vl_data["bays"].items():
                    # Skip empty bays
                    if len(bay_data["equipments"]) == 0:
                        continue

                    # Stocker la position X pour ce bay
                    bay_data["x_position"] = x

                    # Label du bay with special styling for CBO
                    y = vl_data["y_position"]
                    label_color = "#D32F2F" if bay_data.get("is_coupling") else "#666"
                    label_weight = "bold" if bay_data.get("is_coupling") else "normal"
                    label_prefix = "⚡ " if bay_data.get("is_coupling") else ""

                    self.svg_elements.append(f'''
                        <text x="{x}" y="{y + 30}"
                              font-size="12" fill="{label_color}"
                              font-weight="{label_weight}"
                              text-anchor="middle">
                            {label_prefix}{bay_name}
                        </text>
                    ''')

                    x += self.BAY_WIDTH + self.HORIZONTAL_SPACING

    def _draw_equipment(self, organized: Dict):
        """Dessine les équipements (rectangles avec labels)"""
        for substation in organized.values():
            for vl_data in substation["voltage_levels"].values():
                # Skip if no y_position (means voltage level was skipped)
                if "y_position" not in vl_data:
                    continue

                for bay_data in vl_data["bays"].values():
                    # Skip if no x_position (means bay was skipped)
                    if "x_position" not in bay_data:
                        continue

                    y_eq = vl_data["y_position"] + 50
                    x = bay_data["x_position"]

                    for equipment in bay_data["equipments"]:
                        eq_type = equipment["type"]
                        color = self.EQUIPMENT_COLORS.get(eq_type, self.EQUIPMENT_COLORS["DEFAULT"])

                        # Rectangle pour l'équipement
                        rect_x = x - self.EQUIPMENT_WIDTH / 2
                        self.svg_elements.append(f'''
                            <rect x="{rect_x}" y="{y_eq}"
                                  width="{self.EQUIPMENT_WIDTH}"
                                  height="{self.EQUIPMENT_HEIGHT}"
                                  fill="{color}"
                                  stroke="#333" stroke-width="2"
                                  rx="5"/>
                        ''')

                        # Label type d'équipement
                        text_y = y_eq + self.EQUIPMENT_HEIGHT / 2 - 5
                        self.svg_elements.append(f'''
                            <text x="{x}" y="{text_y}"
                                  font-size="10" font-weight="bold"
                                  text-anchor="middle" fill="#333">
                                {eq_type}
                            </text>
                        ''')

                        # Label nom d'équipement
                        name_y = y_eq + self.EQUIPMENT_HEIGHT / 2 + 8
                        name_truncated = equipment["name"][:12]
                        self.svg_elements.append(f'''
                            <text x="{x}" y="{name_y}"
                                  font-size="9"
                                  text-anchor="middle" fill="#333">
                                {name_truncated}
                            </text>
                        ''')

                        # Ligne verticale connectant au jeu de barres
                        self.svg_elements.append(f'''
                            <line x1="{x}" y1="{vl_data['y_position']}"
                                  x2="{x}" y2="{y_eq}"
                                  stroke="#666" stroke-width="2"/>
                        ''')

                        y_eq += self.EQUIPMENT_HEIGHT + self.VERTICAL_SPACING

    def _draw_connectivity(self, organized: Dict):
        """Dessine les connexions entre équipements (simplified)"""
        # Pour l'instant, les connexions sont implicites via les lignes verticales
        # On pourrait ajouter des connexions horizontales entre équipements si nécessaire
        pass

    def _build_svg(self) -> str:
        """Assemble tous les éléments en un SVG complet"""
        svg_header = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{self.width}"
     height="{self.height}"
     viewBox="0 0 {self.width} {self.height}">

    <!-- Background -->
    <rect width="{self.width}" height="{self.height}" fill="#f5f5f5"/>

    <!-- Title -->
    <text x="{self.width/2}" y="30"
          font-size="24" font-weight="bold"
          text-anchor="middle" fill="#333">
        Single Line Diagram (Simple POC)
    </text>

    <!-- Legend -->
    <g id="legend" transform="translate(20, {self.height - 220})">
        <rect x="-10" y="-10" width="120" height="210" fill="white" stroke="#ddd" stroke-width="1" rx="4" opacity="0.95"/>
        <text x="0" y="10" font-size="12" font-weight="bold">Legend</text>
'''

        # Ajouter la légende
        legend_y = 30
        for eq_type, color in list(self.EQUIPMENT_COLORS.items())[:9]:  # Top 9
            svg_header += f'''
        <rect x="0" y="{legend_y}" width="15" height="15" fill="{color}" stroke="#333"/>
        <text x="20" y="{legend_y + 12}" font-size="10">{eq_type}</text>
'''
            legend_y += 20

        svg_header += '''
    </g>

    <!-- Main diagram -->
    <g id="diagram">
'''

        svg_footer = '''
    </g>
</svg>'''

        return svg_header + '\n'.join(self.svg_elements) + svg_footer


def generate_simple_svg(topology_data: Dict) -> str:
    """
    Fonction helper pour générer un SVG simple

    Args:
        topology_data: Données extraites par les requêtes SPARQL

    Returns:
        String SVG
    """
    generator = SimpleSVGGenerator()
    return generator.generate(topology_data)
