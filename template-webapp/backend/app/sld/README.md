# Single Line Diagram (SLD) Generator

## Architecture modulaire par namespace

Ce module génère des schémas unifilaires à partir des données IEC 61850 en RDF. Il utilise une **architecture modulaire par namespace** pour supporter les conventions de différents GRT (Gestionnaires de Réseau de Transport).

## Pourquoi des namespaces par GRT ?

Chaque GRT a ses propres conventions de représentation des schémas unifilaires :

### Exemple : Différences RTE vs autres GRT

| Aspect | RTE (France) | Autre GRT potentiel |
|--------|--------------|---------------------|
| **Départ 1/2 DJ** | ❌ Interdit | ✅ Autorisé |
| **JdB orientation** | Toujours horizontal | Peut être vertical |
| **Couplage barres** | Sur le côté (gauche/droite) | Peut être au centre |
| **Sections JdB** | Support omnibus/sections | Peut ne pas gérer |

## Structure du code

```
app/sld/
├── __init__.py                 # Point d'entrée du module
├── README.md                   # Cette documentation
├── rte_rules.py               # Namespace RTE (conventions France)
├── base_namespace.py          # Classe abstraite pour les namespaces (future)
├── layout_engine.py           # Moteur de calcul de layout (future)
└── svg_renderer.py            # Générateur SVG (future)
```

## Namespace RTE : Conventions

### 1. Jeux de barres (Busbars)

```
═══════════════════════════════════
        JdB 101 (90kV)

═══════════════════════════════════
        JdB 102 (90kV)

═══════════════════════════════════
        JdB 103 (90kV)
```

**Règles** :
- Toujours **horizontaux**
- **Empilés verticalement** (101 en haut, puis 102, 103)
- Espacement : `busbar_vertical_spacing = 200px`

### 2. Départs standards

```
        ═══════════════════════════════════
               JdB 101
                │
               [SA]  ← Sectionneur d'aiguillage
                │
               [DJ]  ← Disjoncteur
                │
            [TC][TT] ← Transformateurs de mesure
                │
                ▼
             LIGNE 1
```

**Règles** :
- Un départ = **un seul JdB** (pas de 1/2 disjoncteur)
- Ordre vertical des équipements défini dans `equipment_layers`
- Espacement horizontal : `bay_horizontal_spacing = 150px`

### 3. Couplage de barres (CBO)

Le CBO connecte deux jeux de barres. Selon les conventions RTE, il est positionné **sur le côté** :

```
    CBO ──┐
    │     │
   [SA1]  │  ═══════════════  JdB 101
    │     │
   [DJ]   │
    │     │
   [SA2]  │  ═══════════════  JdB 102
    │     │
    └─────┘
```

**Règles** :
- Position : `coupling_position = "left"` ou `"right"`
- Largeur réservée : `coupling_width = 100px`
- Équipements du CBO : DJ + sectionneurs (SA)

### 4. Sections de barres / Omnibus

Un jeu de barres peut être divisé en plusieurs sections :

```
═══════════ ╪ ═══════════ ╪ ═══════════
  Section A     Section B     Section C
                   ↑
            Séparateur (sectionneur)
```

**Règles** :
- `busbar_sections_enabled = True`
- Largeur du séparateur : `section_separator_width = 30px`
- Chaque section a ses propres départs

### 5. Ordre des équipements (Layers)

Ordre vertical standard RTE dans un départ :

```python
equipment_layers = {
    "BUSBAR": 0,      # Jeu de barres
    "DIS_SA": 1,      # Sectionneur d'aiguillage (connexion JdB)
    "DIS_SL": 2,      # Sectionneur de ligne
    "CBR": 3,         # Disjoncteur
    "DIS_ST": 4,      # Sectionneur de terre
    "CTR": 5,         # Transformateur de courant
    "VTR": 5,         # Transformateur de tension (même niveau)
    "TERMINAL": 6     # Point de départ (ligne/transfo)
}
```

## Types d'équipements RTE

### Sectionneurs (DIS)

RTE utilise des sous-types de sectionneurs :

| Code | Type | Description | Position typique |
|------|------|-------------|------------------|
| **SA** | Sectionneur d'Aiguillage | Connexion au JdB | Layer 1 (en haut) |
| **SL** | Sectionneur de Ligne | Sectionneur aval | Layer 2 |
| **ST** | Sectionneur de Terre | Mise à la terre | Layer 4 (en bas) |
| **SS** | Sectionneur de Sectionnement | Sépare sections JdB | Dans le JdB |

Ces types sont extraits du champ `<Private type="RTE-ConductingEquipmentType">`.

## Exemple d'utilisation

```python
from app.sld import RTE_NAMESPACE

# Récupérer les règles
rules = RTE_NAMESPACE.rules

# Obtenir la position Y d'un jeu de barres
y_pos = RTE_NAMESPACE.get_busbar_y_position("101")  # → 0
y_pos = RTE_NAMESPACE.get_busbar_y_position("102")  # → 200
y_pos = RTE_NAMESPACE.get_busbar_y_position("103")  # → 400

# Obtenir le layer d'un équipement
layer = RTE_NAMESPACE.get_equipment_layer("CBR")           # → 3
layer = RTE_NAMESPACE.get_equipment_layer("DIS", "SA")     # → 1
layer = RTE_NAMESPACE.get_equipment_layer("CTR")           # → 5

# Vérifier si le couplage est à gauche
if RTE_NAMESPACE.should_render_coupling_left():
    # Dessiner le CBO à gauche
    pass
```

## Extension future : Autres GRT

Pour ajouter le support d'un autre GRT (par exemple ELIA en Belgique) :

1. Créer `elia_rules.py` avec les conventions ELIA
2. Implémenter les différences (départs 1/2 DJ, orientation JdB, etc.)
3. Instancier : `ELIA_NAMESPACE = ELIARenderingNamespace()`
4. Utiliser le namespace approprié selon le fichier SCD

```python
# Détection automatique selon le fichier
if scl_file.contains("RTE"):
    namespace = RTE_NAMESPACE
elif scl_file.contains("ELIA"):
    namespace = ELIA_NAMESPACE
else:
    namespace = DEFAULT_NAMESPACE
```

## Prochaines étapes

1. ✅ Définir les règles RTE (`rte_rules.py`)
2. ⏳ Créer la bibliothèque de symboles SVG (`svg_symbols.py`)
3. ⏳ Implémenter le moteur de layout (`layout_engine.py`)
4. ⏳ Développer le renderer SVG (`svg_renderer.py`)
5. ⏳ Créer l'API endpoint pour générer les SLD
6. ⏳ Intégrer dans le frontend

## Références

- **IEC 61850** : Standard pour la communication dans les postes électriques
- **COMPAS-Topo** : Extension RTE pour les informations topologiques
- **CIM** : Common Information Model (peut être utilisé pour d'autres GRT)
