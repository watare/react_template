"""
Script pour extraire les symboles essentiels depuis QElectroTech
"""

from pathlib import Path
from qet_converter import convert_qet_symbol
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Symboles à extraire
SYMBOLS_TO_EXTRACT = {
    "CBR": "10_electric/10_allpole/450_high_voltage/disjoncteur_dm1-a.elmt",
    "DIS": "10_electric/10_allpole/450_high_voltage/sectionneur_3_positions.elmt",
    # On va les trouver
}

def find_symbols(qet_repo_path: Path):
    """Trouve les symboles dans le repo QET"""

    logger.info("Searching for symbols in QET repository...")

    found_symbols = {}

    # Chercher disjoncteur (circuit breaker)
    breakers = list(qet_repo_path.rglob("*disjoncteur*.elmt"))
    if breakers:
        # Prendre le premier disjoncteur haute tension
        for b in breakers:
            if 'high_voltage' in str(b) or '450' in str(b):
                found_symbols["CBR"] = b
                logger.info(f"✅ Found circuit breaker: {b.name}")
                break
        if "CBR" not in found_symbols and breakers:
            found_symbols["CBR"] = breakers[0]
            logger.info(f"✅ Found circuit breaker: {breakers[0].name}")

    # Chercher sectionneur (disconnector)
    disconnectors = list(qet_repo_path.rglob("*sectionneur*.elmt"))
    if disconnectors:
        for d in disconnectors:
            if '3_position' in str(d) or 'high_voltage' in str(d):
                found_symbols["DIS"] = d
                logger.info(f"✅ Found disconnector: {d.name}")
                break
        if "DIS" not in found_symbols and disconnectors:
            found_symbols["DIS"] = disconnectors[0]
            logger.info(f"✅ Found disconnector: {disconnectors[0].name}")

    # Chercher transformateur de courant (current transformer)
    ct_patterns = ["*tc*.elmt", "*transfo*courant*.elmt", "*current*trans*.elmt"]
    for pattern in ct_patterns:
        cts = list(qet_repo_path.rglob(pattern))
        if cts:
            found_symbols["CTR"] = cts[0]
            logger.info(f"✅ Found current transformer: {cts[0].name}")
            break

    # Chercher transformateur de tension (voltage transformer)
    vt_patterns = ["*tt*.elmt", "*transfo*tension*.elmt", "*voltage*trans*.elmt"]
    for pattern in vt_patterns:
        vts = list(qet_repo_path.rglob(pattern))
        if vts:
            found_symbols["VTR"] = vts[0]
            logger.info(f"✅ Found voltage transformer: {vts[0].name}")
            break

    # Chercher transformateur de puissance (power transformer)
    pt_patterns = ["*transformateur*.elmt", "*power*trans*.elmt"]
    for pattern in pt_patterns:
        pts = list(qet_repo_path.rglob(pattern))
        if pts:
            # Éviter les CT/VT
            for pt in pts:
                if 'courant' not in str(pt).lower() and 'tension' not in str(pt).lower():
                    found_symbols["PTR"] = pt
                    logger.info(f"✅ Found power transformer: {pt.name}")
                    break
            if "PTR" in found_symbols:
                break

    return found_symbols


def extract_and_save_symbols(qet_repo_path: Path, output_dir: Path):
    """Extrait et sauvegarde les symboles en SVG"""

    output_dir.mkdir(parents=True, exist_ok=True)

    # Trouver les symboles
    symbols_paths = find_symbols(qet_repo_path)

    logger.info(f"\nFound {len(symbols_paths)} symbols")

    # Convertir chaque symbole
    symbols_library = {}

    for symbol_type, elmt_path in symbols_paths.items():
        logger.info(f"\nConverting {symbol_type} from {elmt_path.name}...")

        try:
            symbol = convert_qet_symbol(elmt_path)

            if symbol:
                # Sauvegarder le SVG
                svg_path = output_dir / f"{symbol_type}.svg"
                svg_content = symbol.get_normalized_svg()

                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)

                logger.info(f"✅ Saved to {svg_path}")

                # Ajouter à la bibliothèque
                symbols_library[symbol_type] = {
                    "name": symbol.name,
                    "file": f"{symbol_type}.svg",
                    "width": symbol.width,
                    "height": symbol.height,
                    "terminals": [
                        {
                            "x": t.x - symbol.hotspot_x,  # Normaliser au hotspot
                            "y": t.y - symbol.hotspot_y,
                            "orientation": t.orientation
                        }
                        for t in symbol.terminals
                    ]
                }
            else:
                logger.error(f"❌ Failed to convert {symbol_type}")

        except Exception as e:
            logger.error(f"❌ Error converting {symbol_type}: {e}")

    # Sauvegarder la bibliothèque JSON
    library_path = output_dir / "symbols_library.json"
    with open(library_path, 'w', encoding='utf-8') as f:
        json.dump(symbols_library, f, indent=2)

    logger.info(f"\n✅ Symbols library saved to {library_path}")
    logger.info(f"Extracted {len(symbols_library)}/{len(symbols_paths)} symbols")

    return symbols_library


if __name__ == "__main__":
    # Chemins
    qet_repo = Path("/home/aurelien/mooc/template-webapp/backend/temp_qet_symbols")
    output_dir = Path("/home/aurelien/mooc/template-webapp/backend/app/sld/symbols/svg")

    if not qet_repo.exists():
        logger.error(f"QET repository not found at {qet_repo}")
        exit(1)

    # Extraire
    library = extract_and_save_symbols(qet_repo, output_dir)

    print("\n" + "="*60)
    print("SYMBOLS EXTRACTED:")
    for symbol_type, info in library.items():
        print(f"  {symbol_type}: {info['name']}")
    print("="*60)
