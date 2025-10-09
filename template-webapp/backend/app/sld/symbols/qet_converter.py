"""
QElectroTech Symbol Converter
Convertit les fichiers .elmt (QElectroTech) en SVG pur

Format .elmt:
<definition>
    <names>...</names>
    <description>
        <line x1="..." y1="..." .../>
        <polygon .../>
        <terminal .../>  ← Points de connexion
    </description>
</definition>
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Terminal:
    """Point de connexion d'un symbole"""
    x: float
    y: float
    orientation: str  # 'n', 's', 'e', 'w'
    uuid: str


@dataclass
class Symbol:
    """Symbole électrique converti"""
    name: str
    svg_content: str
    width: float
    height: float
    hotspot_x: float  # Point d'ancrage X
    hotspot_y: float  # Point d'ancrage Y
    terminals: List[Terminal]

    def get_normalized_svg(self) -> str:
        """
        Retourne le SVG normalisé (centré sur le hotspot)
        Le hotspot devient (0, 0)
        """
        # Créer un viewBox centré sur le hotspot
        viewbox_x = -self.hotspot_x
        viewbox_y = -self.hotspot_y

        return f'''<svg xmlns="http://www.w3.org/2000/svg"
                     width="{self.width}"
                     height="{self.height}"
                     viewBox="{viewbox_x} {viewbox_y} {self.width} {self.height}">
    {self.svg_content}
</svg>'''


class QETConverter:
    """Convertisseur .elmt → SVG"""

    # Mapping des éléments QET → SVG
    ELEMENT_MAPPINGS = {
        'line': 'line',
        'polygon': 'polyline',
        'ellipse': 'ellipse',
        'circle': 'circle',
        'arc': 'path',
        'rect': 'rect',
        'text': 'text'
    }

    # Style attributes mapping
    STYLE_MAPPINGS = {
        'line-style': {
            'normal': 'solid',
            'dashed': '5,5',
            'dotted': '2,2'
        },
        'line-weight': {
            'normal': '1',
            'thin': '0.5',
            'strong': '2'
        }
    }

    def convert_file(self, elmt_path: Path) -> Optional[Symbol]:
        """
        Convertit un fichier .elmt en Symbol

        Args:
            elmt_path: Chemin vers le fichier .elmt

        Returns:
            Symbol converti ou None si erreur
        """
        try:
            tree = ET.parse(elmt_path)
            root = tree.getroot()

            # Extraire métadonnées
            width = float(root.get('width', 40))
            height = float(root.get('height', 60))
            hotspot_x = float(root.get('hotspot_x', 20))
            hotspot_y = float(root.get('hotspot_y', 30))

            # Extraire le nom
            name = self._extract_name(root)

            # Convertir la description en SVG
            description = root.find('description')
            if description is None:
                logger.warning(f"No description found in {elmt_path}")
                return None

            svg_elements = []
            terminals = []

            for elem in description:
                if elem.tag == 'terminal':
                    # Extraire terminal
                    terminal = self._extract_terminal(elem)
                    if terminal:
                        terminals.append(terminal)
                else:
                    # Convertir en SVG
                    svg_elem = self._convert_element(elem)
                    if svg_elem:
                        svg_elements.append(svg_elem)

            svg_content = '\n'.join(svg_elements)

            return Symbol(
                name=name,
                svg_content=svg_content,
                width=width,
                height=height,
                hotspot_x=hotspot_x,
                hotspot_y=hotspot_y,
                terminals=terminals
            )

        except Exception as e:
            logger.error(f"Error converting {elmt_path}: {e}")
            return None

    def _extract_name(self, root: ET.Element) -> str:
        """Extrait le nom du symbole (préfère anglais ou français)"""
        names = root.find('names')
        if names is None:
            return "Unknown"

        # Chercher nom en anglais
        for name in names.findall('name'):
            if name.get('lang') == 'en':
                return name.text or "Unknown"

        # Fallback français
        for name in names.findall('name'):
            if name.get('lang') == 'fr':
                return name.text or "Unknown"

        # Premier disponible
        first_name = names.find('name')
        return first_name.text if first_name is not None else "Unknown"

    def _extract_terminal(self, elem: ET.Element) -> Optional[Terminal]:
        """Extrait un terminal"""
        try:
            return Terminal(
                x=float(elem.get('x', 0)),
                y=float(elem.get('y', 0)),
                orientation=elem.get('orientation', 'n'),
                uuid=elem.get('uuid', '')
            )
        except (ValueError, TypeError):
            return None

    def _convert_element(self, elem: ET.Element) -> Optional[str]:
        """Convertit un élément QET en SVG"""
        tag = elem.tag

        if tag == 'line':
            return self._convert_line(elem)
        elif tag == 'polygon':
            return self._convert_polygon(elem)
        elif tag == 'ellipse':
            return self._convert_ellipse(elem)
        elif tag == 'circle':
            return self._convert_circle(elem)
        elif tag == 'arc':
            return self._convert_arc(elem)
        elif tag == 'rect':
            return self._convert_rect(elem)
        elif tag == 'dynamic_text' or tag == 'text':
            # On ignore les textes dynamiques (labels)
            return None
        else:
            logger.debug(f"Unsupported element: {tag}")
            return None

    def _convert_line(self, elem: ET.Element) -> str:
        """Convertit une ligne"""
        x1 = elem.get('x1', '0')
        y1 = elem.get('y1', '0')
        x2 = elem.get('x2', '0')
        y2 = elem.get('y2', '0')

        style = self._extract_style(elem)

        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {style}/>'

    def _convert_polygon(self, elem: ET.Element) -> str:
        """Convertit un polygone"""
        points = []

        # Extraire tous les points x1,y1 x2,y2 x3,y3...
        i = 1
        while True:
            x = elem.get(f'x{i}')
            y = elem.get(f'y{i}')
            if x is None or y is None:
                break
            points.append(f"{x},{y}")
            i += 1

        if not points:
            return ""

        points_str = ' '.join(points)
        closed = elem.get('closed', 'true') == 'true'
        style = self._extract_style(elem)

        if closed:
            return f'<polygon points="{points_str}" {style}/>'
        else:
            return f'<polyline points="{points_str}" {style}/>'

    def _convert_ellipse(self, elem: ET.Element) -> str:
        """Convertit une ellipse"""
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        width = float(elem.get('width', 10))
        height = float(elem.get('height', 10))

        # Centre de l'ellipse
        cx = x + width / 2
        cy = y + height / 2
        rx = width / 2
        ry = height / 2

        style = self._extract_style(elem)

        return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" {style}/>'

    def _convert_circle(self, elem: ET.Element) -> str:
        """Convertit un cercle"""
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        diameter = float(elem.get('diameter', 10))

        cx = x + diameter / 2
        cy = y + diameter / 2
        r = diameter / 2

        style = self._extract_style(elem)

        return f'<circle cx="{cx}" cy="{cy}" r="{r}" {style}/>'

    def _convert_arc(self, elem: ET.Element) -> str:
        """Convertit un arc en path SVG"""
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        width = float(elem.get('width', 10))
        height = float(elem.get('height', 10))
        start_angle = float(elem.get('start', 0))
        span_angle = float(elem.get('angle', 90))

        # Conversion arc QET → path SVG (simplifié)
        # TODO: Conversion précise si nécessaire
        style = self._extract_style(elem)

        # Pour l'instant, on retourne un placeholder
        return f'<!-- arc: x={x} y={y} start={start_angle} span={span_angle} -->'

    def _convert_rect(self, elem: ET.Element) -> str:
        """Convertit un rectangle"""
        x = elem.get('x', '0')
        y = elem.get('y', '0')
        width = elem.get('width', '10')
        height = elem.get('height', '10')
        rx = elem.get('rx', '0')

        style = self._extract_style(elem)

        return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" {style}/>'

    def _extract_style(self, elem: ET.Element) -> str:
        """Extrait le style d'un élément"""
        style_str = elem.get('style', '')

        if not style_str:
            return 'stroke="black" stroke-width="1" fill="none"'

        # Parser le style QET
        style_parts = {}
        for part in style_str.split(';'):
            if ':' in part:
                key, value = part.split(':', 1)
                style_parts[key] = value

        # Convertir en SVG
        svg_attrs = []

        # Stroke
        color = style_parts.get('color', 'black')
        svg_attrs.append(f'stroke="{color}"')

        # Stroke width
        line_weight = style_parts.get('line-weight', 'normal')
        stroke_width = self.STYLE_MAPPINGS['line-weight'].get(line_weight, '1')
        svg_attrs.append(f'stroke-width="{stroke_width}"')

        # Stroke dasharray
        line_style = style_parts.get('line-style', 'normal')
        if line_style != 'normal':
            dasharray = self.STYLE_MAPPINGS['line-style'].get(line_style, '')
            if dasharray:
                svg_attrs.append(f'stroke-dasharray="{dasharray}"')

        # Fill
        filling = style_parts.get('filling', 'none')
        svg_attrs.append(f'fill="{filling}"')

        return ' '.join(svg_attrs)


def convert_qet_symbol(elmt_path: Path) -> Optional[Symbol]:
    """
    Fonction helper pour convertir un symbole QET

    Args:
        elmt_path: Chemin vers le fichier .elmt

    Returns:
        Symbol converti
    """
    converter = QETConverter()
    return converter.convert_file(elmt_path)
