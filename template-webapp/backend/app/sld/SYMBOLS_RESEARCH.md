# Recherche sur les bibliothèques de symboles électriques

## Objectif

Trouver une bibliothèque de symboles SVG pour les équipements IEC 61850 :
- Disjoncteurs (CBR)
- Sectionneurs (DIS)
- Transformateurs de courant (CTR)
- Transformateurs de tension (VTR)
- Transformateurs de puissance (PTR)
- Jeux de barres

## Options disponibles

### 1. QElectroTech (⭐ Recommandé)

**URL** : https://qelectrotech.org/
**Licence** : GPL v2 (open-source)
**Format** : `.elmt` (XML) + SVG intégré

**Avantages** :
- ✅ Bibliothèque complète de symboles HTA/HTB
- ✅ Symboles normalisés IEC
- ✅ Format ouvert (XML avec SVG)
- ✅ Utilisé par des utilities réelles
- ✅ Symboles pour postes électriques

**Inconvénients** :
- ⚠️ Format propriétaire `.elmt` (mais convertible)
- ⚠️ Nécessite extraction/conversion

**Symboles disponibles** :
```
- circuit_breakers/
  - circuit_breaker_iec.elmt
  - circuit_breaker_sf6.elmt
- disconnectors/
  - disconnector_3_positions.elmt
  - disconnector_with_earth.elmt
- transformers/
  - current_transformer.elmt
  - voltage_transformer.elmt
  - power_transformer_2_windings.elmt
  - power_transformer_3_windings.elmt
- busbars/
  - busbar_single.elmt
  - busbar_double.elmt
```

### 2. CIM Graphics (IEC 61970-453)

**URL** : Partie de la norme CIM
**Licence** : Norme IEC (payante mais profils publics existent)
**Format** : SVG Profile

**Avantages** :
- ✅ Standard industriel pour TSO/DSO
- ✅ Interopérabilité garantie
- ✅ Conçu spécifiquement pour schémas unifilaires

**Inconvénients** :
- ❌ Norme payante
- ❌ Moins de bibliothèques gratuites
- ⚠️ Complexe à implémenter

**Note** : RTE utilise probablement un profil basé sur CIM pour ses propres outils.

### 3. Electrical Symbols (GitHub - Open Source)

**URL** : https://github.com/qelectrotech/qelectrotech-elements
**Licence** : GPL/CC-BY
**Format** : SVG pur

**Avantages** :
- ✅ SVG pur (facile à intégrer)
- ✅ Open-source
- ✅ Modifiable

**Inconvénients** :
- ⚠️ Moins complet que QElectroTech
- ⚠️ Qualité variable selon les symboles

### 4. Créer nos propres symboles (dernier recours)

**Avantages** :
- ✅ Contrôle total
- ✅ Optimisé pour notre use case
- ✅ Style cohérent

**Inconvénients** :
- ❌ Beaucoup de travail
- ❌ Risque d'erreurs
- ❌ Maintenance

## Recommandation

### ⭐ Solution recommandée : PowSyBl (RTE Open Source)

**URL** : https://github.com/powsybl/powsybl-diagram

**Pourquoi PowSyBl** :
- ✅ **Développé par RTE** → Conventions RTE natives !
- ✅ **Support CIM/CGMES** complet
- ✅ **Génération SVG** de schémas unifilaires
- ✅ **Bibliothèque de symboles** intégrée
- ✅ **Layout automatique** avec 3 modes (auto, semi-auto, CGMES DL)
- ✅ **Open-source** (Mozilla Public License 2.0)
- ✅ **Production-ready** (utilisé par RTE en production)

**Architecture PowSyBl** :
```
powsybl-diagram (Java)
├── single-line-diagram/
│   ├── svg-components/      ← Bibliothèque de symboles SVG
│   ├── layout/              ← Algorithmes de layout
│   └── metadata/            ← Infos CIM/CGMES
└── network-area-diagram/
```

### Alternative : QElectroTech (Fallback)

Si on a besoin de symboles supplémentaires non couverts par PowSyBl :

1. **Base** : Utiliser QElectroTech comme bibliothèque complémentaire
2. **Extraction** : Convertir les `.elmt` en SVG purs
3. **Adaptation** : Ajuster si nécessaire pour conventions RTE
4. **Compléments** : Créer uniquement les symboles manquants

### Plan d'implémentation

#### Phase 1 : Extraction QElectroTech
```bash
# Cloner le repository QElectroTech
git clone https://github.com/qelectrotech/qelectrotech-elements.git

# Structure des symboles
elements/
├── 10_electric/
│   ├── 10_allpole/
│   │   ├── 380_signalisation/
│   │   └── 390_sensors_transmitters/
│   ├── 20_manufacturers_articles/
│   └── ...
└── ...
```

#### Phase 2 : Convertisseur .elmt → SVG
```python
def extract_svg_from_elmt(elmt_path):
    """
    Extrait le SVG d'un fichier .elmt QElectroTech

    Format .elmt :
    <definition>
        <svg ...>
            <!-- Contenu SVG du symbole -->
        </svg>
        <terminals>
            <terminal x="0" y="-17" />
            <terminal x="0" y="17" />
        </terminals>
    </definition>
    """
    tree = ET.parse(elmt_path)
    svg_element = tree.find('.//svg')
    terminals = tree.findall('.//terminal')

    return {
        'svg': ET.tostring(svg_element),
        'terminals': [(t.get('x'), t.get('y')) for t in terminals]
    }
```

#### Phase 3 : Bibliothèque de symboles
```python
# backend/app/sld/symbols/
symbols/
├── __init__.py
├── qet_converter.py          # Convertisseur .elmt → JSON
├── symbol_library.json       # Bibliothèque centralisée
└── svg/
    ├── CBR_iec.svg           # Disjoncteur IEC
    ├── DIS_3pos.svg          # Sectionneur 3 positions
    ├── CTR_single.svg        # TC simple
    ├── VTR_single.svg        # TT simple
    └── PTR_2winding.svg      # Transfo 2 enroulements
```

#### Phase 4 : Mapping IEC 61850 → Symboles
```python
EQUIPMENT_SYMBOL_MAPPING = {
    "CBR": "CBR_iec.svg",
    "DIS": {
        "SA": "DIS_3pos.svg",        # Sectionneur aiguillage
        "SL": "DIS_3pos.svg",        # Sectionneur ligne
        "ST": "DIS_earth.svg",       # Sectionneur de terre
        "SS": "DIS_3pos.svg"         # Sectionneur sectionnement
    },
    "CTR": "CTR_single.svg",
    "VTR": "VTR_single.svg",
    "PTR": "PTR_2winding.svg"
}
```

## Exemple de symbole QElectroTech

Voici un exemple de fichier `.elmt` (simplifié) :

```xml
<definition type="element">
    <names>
        <name lang="en">Circuit breaker</name>
        <name lang="fr">Disjoncteur</name>
    </names>

    <elementInformations/>

    <informations>IEC standard circuit breaker symbol</informations>

    <description>
        <line x1="0" y1="-17" x2="0" y2="-10" />
        <rect x="-5" y="-10" width="10" height="20" />
        <line x1="0" y1="10" x2="0" y2="17" />

        <terminal x="0" y="-17" orientation="n"/>
        <terminal x="0" y="17" orientation="s"/>
    </description>
</definition>
```

**Extraction SVG** :
```svg
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="40">
  <line x1="10" y1="0" x2="10" y2="7" stroke="black" stroke-width="2"/>
  <rect x="5" y="7" width="10" height="20" fill="white" stroke="black" stroke-width="2"/>
  <line x1="10" y1="27" x2="10" y2="34" stroke="black" stroke-width="2"/>
</svg>
```

## Symboles spécifiques RTE

Certains symboles peuvent avoir des variantes RTE. Dans ce cas :

1. **Utiliser la base QElectroTech**
2. **Créer une variante RTE** si nécessaire (ex: style graphique légèrement différent)
3. **Documenter les différences** dans le namespace RTE

Exemple :
```python
# rte_rules.py
RTE_SYMBOL_OVERRIDES = {
    "CBR": "CBR_rte_variant.svg",  # Variante RTE si différente
    # Sinon, utiliser symbole standard
}
```

## Ressources

- **QElectroTech** : https://qelectrotech.org/
- **QET Elements (GitHub)** : https://github.com/qelectrotech/qelectrotech-elements
- **IEC 61850-6** : Symboles et conventions (norme officielle)
- **IEC 61970-453** : CIM Graphics Profile
- **Wikipedia IEC symbols** : https://en.wikipedia.org/wiki/Electronic_symbol

## Prochaine action

✅ **Décision** : Utiliser QElectroTech comme base
⏳ **TODO** : Créer le convertisseur `.elmt` → SVG
⏳ **TODO** : Extraire les symboles nécessaires (CBR, DIS, CTR, VTR, PTR)
⏳ **TODO** : Créer la bibliothèque `symbol_library.json`
