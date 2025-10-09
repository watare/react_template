"""
Symbol Library - Bibliothèque de symboles SVG pour SLD
Charge les symboles depuis le fichier symbols_library.json
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SymbolTerminal:
    """Point de connexion d'un symbole"""
    x: float
    y: float
    orientation: str  # 'n', 's', 'e', 'w'


@dataclass
class SymbolDefinition:
    """Définition d'un symbole électrique"""
    name: str
    file: str
    width: float
    height: float
    terminals: List[SymbolTerminal]
    svg_content: Optional[str] = None


class SymbolLibrary:
    """
    Bibliothèque de symboles SVG

    Charge les symboles depuis symbols_library.json
    et fournit des méthodes pour récupérer les SVG
    """

    def __init__(self, symbols_dir: Optional[Path] = None):
        """
        Initialise la bibliothèque

        Args:
            symbols_dir: Répertoire contenant les symboles
                        (par défaut: même répertoire que ce fichier /svg/)
        """
        if symbols_dir is None:
            symbols_dir = Path(__file__).parent / "svg"

        self.symbols_dir = symbols_dir
        self.symbols: Dict[str, SymbolDefinition] = {}
        self._load_library()

    def _load_library(self):
        """Charge la bibliothèque de symboles"""
        library_path = self.symbols_dir / "symbols_library.json"

        if not library_path.exists():
            logger.warning(f"Symbols library not found at {library_path}")
            return

        try:
            with open(library_path, 'r', encoding='utf-8') as f:
                library_data = json.load(f)

            for symbol_type, symbol_info in library_data.items():
                terminals = [
                    SymbolTerminal(**t)
                    for t in symbol_info.get('terminals', [])
                ]

                self.symbols[symbol_type] = SymbolDefinition(
                    name=symbol_info['name'],
                    file=symbol_info['file'],
                    width=symbol_info['width'],
                    height=symbol_info['height'],
                    terminals=terminals
                )

            logger.info(f"Loaded {len(self.symbols)} symbols from library")

        except Exception as e:
            logger.error(f"Error loading symbols library: {e}")

    def get_symbol_svg(self, symbol_type: str, subtype: str = "") -> str:
        """
        Récupère le SVG d'un symbole

        Args:
            symbol_type: Type de symbole (CBR, DIS, CTR, VTR, PTR)
            subtype: Sous-type (pour les sectionneurs: SA, SL, ST, SS)

        Returns:
            Contenu SVG du symbole
        """
        # Construire la clé (ex: "DIS_SA" ou "CBR")
        key = f"{symbol_type}_{subtype}" if subtype else symbol_type

        # Chercher avec sous-type d'abord
        if key in self.symbols:
            return self._load_symbol_content(key)

        # Fallback sur type seul
        if symbol_type in self.symbols:
            return self._load_symbol_content(symbol_type)

        # Symbole par défaut si non trouvé
        logger.warning(f"Symbol {key} not found, using default")
        return self._get_default_symbol(symbol_type)

    def _load_symbol_content(self, symbol_type: str) -> str:
        """Charge le contenu SVG d'un symbole depuis le fichier"""
        symbol = self.symbols[symbol_type]

        # Cache le contenu si pas déjà fait
        if symbol.svg_content is None:
            svg_path = self.symbols_dir / symbol.file

            if not svg_path.exists():
                logger.error(f"Symbol file not found: {svg_path}")
                return self._get_default_symbol(symbol_type)

            try:
                with open(svg_path, 'r', encoding='utf-8') as f:
                    symbol.svg_content = f.read()
            except Exception as e:
                logger.error(f"Error loading symbol {svg_path}: {e}")
                return self._get_default_symbol(symbol_type)

        return symbol.svg_content

    def _get_default_symbol(self, symbol_type: str) -> str:
        """Génère un symbole par défaut (rectangle)"""
        return f'''<svg xmlns="http://www.w3.org/2000/svg"
                     width="40" height="60"
                     viewBox="-20 -30 40 60">
    <rect x="-15" y="-25" width="30" height="50"
          fill="white" stroke="black" stroke-width="2"/>
    <text x="0" y="5" text-anchor="middle" font-size="10">
        {symbol_type}
    </text>
</svg>'''

    def get_symbol_info(self, symbol_type: str) -> Optional[SymbolDefinition]:
        """Récupère les informations d'un symbole"""
        return self.symbols.get(symbol_type)

    def list_available_symbols(self) -> List[str]:
        """Liste tous les symboles disponibles"""
        return list(self.symbols.keys())

    def get_symbol_dimensions(self, symbol_type: str) -> tuple[float, float]:
        """
        Récupère les dimensions d'un symbole

        Returns:
            (width, height)
        """
        symbol = self.symbols.get(symbol_type)
        if symbol:
            return (symbol.width, symbol.height)
        return (40.0, 60.0)  # Dimensions par défaut


# Instance globale
_symbol_library_instance = None


def get_symbol_library() -> SymbolLibrary:
    """
    Récupère l'instance globale de la bibliothèque de symboles (singleton)

    Returns:
        SymbolLibrary instance
    """
    global _symbol_library_instance
    if _symbol_library_instance is None:
        _symbol_library_instance = SymbolLibrary()
    return _symbol_library_instance
