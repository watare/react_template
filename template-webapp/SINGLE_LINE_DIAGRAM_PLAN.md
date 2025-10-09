# Plan de génération de schémas unifilaires

## Vue d'ensemble

Ce document décrit le plan complet pour générer des schémas unifilaires (Single Line Diagrams) à partir des fichiers IEC 61850 SCL.

## Architecture complète

```
┌──────────────────────────────────────────────────────────────────┐
│                    Génération de Schéma Unifilaire                │
└──────────────────────────────────────────────────────────────────┘

1. SOURCE : Fichier IEC 61850 SCL
   │
   ├─▶ Conversion SCL → RDF (déjà implémenté)
   │   └─▶ Stockage dans Fuseki
   │
2. CONVERSION : IEC 61850 RDF → CIM RDF
   │
   ├─▶ Transformations SPARQL
   │   ├─ Substation → Substation
   │   ├─ VoltageLevel → VoltageLevel
   │   ├─ Bay → Bay
   │   ├─ ConductingEquipment → Equipment (CBR, DIS, CTR, etc.)
   │   └─ ConnectivityNode + Terminal → Connectivité
   │
   └─▶ Export CIM RDF → CGMES XML
       │
3. GÉNÉRATION SVG : PowSyBl
   │
   ├─▶ Lecture CGMES XML
   ├─▶ Layout automatique (conventions RTE)
   └─▶ Génération SVG
       │
4. AFFICHAGE : Frontend React
   │
   └─▶ Visualisation interactive du SVG
```

## Composants réalisés

### ✅ 1. Namespace RTE pour règles de représentation

**Fichier** : `backend/app/sld/rte_rules.py`

**Contenu** :
- `RTELayoutRules` : Configuration des espacements, ordre des JdB, position du couplage
- `RTEEquipmentSymbol` : Définition des symboles d'équipements
- `BusbarSection` : Gestion des sections/omnibus
- `CouplingBay` : Gestion des couplages de barres (CBO)

**Règles RTE implémentées** :
- ✅ Jeux de barres horizontaux empilés verticalement
- ✅ Pas de départ 1/2 disjoncteur
- ✅ Couplage de barres sur le côté (gauche/droite)
- ✅ Support des sections/omnibus
- ✅ Ordre des équipements (layers) selon conventions RTE

### ✅ 2. Convertisseur IEC 61850 → CIM

**Fichier** : `backend/app/converters/iec61850_to_cim.py`

**Fonctionnalités** :
- Conversion via transformations SPARQL
- Mapping des types d'équipements
- Support des sous-types RTE (SA, SL, ST, SS pour sectionneurs)
- Export CGMES XML
- Préservation de la topologie

**Mapping implémenté** :

| IEC 61850 | CIM | Notes |
|-----------|-----|-------|
| Substation | cim:Substation | ✅ Direct |
| VoltageLevel | cim:VoltageLevel | ✅ Direct |
| Bay | cim:Bay | ✅ Direct |
| CBR | cim:Breaker | Disjoncteur |
| DIS (SA/SL/SS) | cim:Disconnector | Sectionneur |
| DIS (ST) | cim:GroundDisconnector | Sectionneur de terre |
| CTR | cim:CurrentTransformer | TC |
| VTR | cim:PotentialTransformer | TT |
| PTR | cim:PowerTransformer | Transfo puissance |
| Terminal | cim:Terminal | ✅ Direct |
| ConnectivityNode | cim:ConnectivityNode | ✅ Direct |

## Composants à réaliser

### ⏳ 3. Intégration PowSyBl

**Options d'intégration** :

#### Option A : PowSyBl via Docker (Recommandé pour POC)
```yaml
# docker-compose.yml
services:
  powsybl:
    image: powsybl/powsybl-core:latest
    ports:
      - "8080:8080"
    volumes:
      - ./cgmes_files:/data
```

#### Option B : PowSyBl via py4j (Python ↔ Java)
```python
from py4j.java_gateway import JavaGateway

gateway = JavaGateway()
powsybl = gateway.entry_point
svg = powsybl.generateSLD(cgmes_file, layout="cgmes")
```

#### Option C : PowSyBl CLI via subprocess
```python
import subprocess

subprocess.run([
    "powsybl", "single-line-diagram",
    "--input", cgmes_file,
    "--output", svg_file,
    "--layout-mode", "cgmes"
])
```

### ⏳ 4. API Endpoint FastAPI

**Fichier** : `backend/app/api/sld.py`

```python
@router.post("/sld/generate")
async def generate_single_line_diagram(
    file_id: int,
    layout_mode: str = "cgmes",
    db: Session = Depends(get_db)
):
    """
    Génère un schéma unifilaire SVG

    Args:
        file_id: ID du fichier SCL
        layout_mode: Mode de layout (cgmes, automatic, semi-automatic)

    Returns:
        SVG du schéma unifilaire
    """
    # 1. Récupérer le fichier SCL
    scl_file = db.query(SCLFile).filter(SCLFile.id == file_id).first()

    # 2. Charger le graphe IEC 61850 RDF depuis Fuseki
    rdf_client = RDFClient()
    iec_graph = rdf_client.get_graph(scl_file.fuseki_dataset)

    # 3. Convertir IEC 61850 → CIM
    converter = IEC61850ToCIMConverter()
    cim_graph = converter.convert(iec_graph)

    # 4. Exporter en CGMES XML
    cgmes_file = f"/tmp/cgmes_{file_id}.xml"
    converter.export_cgmes_xml(cgmes_file)

    # 5. Appeler PowSyBl pour générer le SVG
    svg = generate_svg_with_powsybl(cgmes_file, layout_mode)

    return {"svg": svg}
```

### ⏳ 5. Frontend : Visualisation SVG

**Composant** : `frontend/src/components/SingleLineDiagramViewer.tsx`

```typescript
interface SingleLineDiagramViewerProps {
  fileId: number;
  layoutMode?: 'cgmes' | 'automatic' | 'semi-automatic';
}

export const SingleLineDiagramViewer: React.FC<SingleLineDiagramViewerProps> = ({
  fileId,
  layoutMode = 'cgmes'
}) => {
  const [svg, setSvg] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const generateDiagram = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/sld/generate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ file_id: fileId, layout_mode: layoutMode })
        }
      );
      const data = await response.json();
      setSvg(data.svg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sld-viewer">
      <button onClick={generateDiagram}>Generate Diagram</button>
      {loading && <p>Generating...</p>}
      {svg && <div dangerouslySetInnerHTML={{ __html: svg }} />}
    </div>
  );
};
```

## Flux de données complet

```
Utilisateur
   │
   │ 1. Upload fichier SCL
   ▼
┌──────────────┐
│   Backend    │  2. Conversion SCL → RDF
│   FastAPI    │  3. Stockage Fuseki
└──────┬───────┘
       │
       │ 4. Request "Generate SLD"
       ▼
┌──────────────────────────┐
│   IEC61850ToCIMConverter │  5. IEC 61850 RDF → CIM RDF
│   (SPARQL transforms)    │  6. Export CGMES XML
└──────┬───────────────────┘
       │
       │ 7. CGMES XML
       ▼
┌──────────────┐
│   PowSyBl    │  8. Layout + Rendering
│   (Docker)   │  9. Generate SVG
└──────┬───────┘
       │
       │ 10. SVG Response
       ▼
┌──────────────┐
│   Frontend   │  11. Display SVG
│   React      │  12. Zoom/Pan interactions
└──────────────┘
```

## Prochaines étapes

### Phase 1 : Tests et validation (2-3 jours)
1. ✅ Créer des tests unitaires pour le convertisseur
2. ✅ Tester avec SCD_POSTE_V1.scd
3. ✅ Valider le CGMES XML généré

### Phase 2 : Intégration PowSyBl (2-3 jours)
1. ⏳ Choisir le mode d'intégration (Docker/py4j/CLI)
2. ⏳ Configurer PowSyBl dans docker-compose
3. ⏳ Créer l'API endpoint /sld/generate
4. ⏳ Tester la génération SVG

### Phase 3 : Frontend (1-2 jours)
1. ⏳ Créer le composant SingleLineDiagramViewer
2. ⏳ Ajouter zoom/pan avec react-svg-pan-zoom
3. ⏳ Intégrer dans l'IED Explorer

### Phase 4 : Amélioration continue
1. ⏳ Support des transformateurs multi-enroulements
2. ⏳ Gestion des couplages de barres (CBO)
3. ⏳ Export PDF/PNG
4. ⏳ Annotations personnalisées

## Références

- **PowSyBl** : https://github.com/powsybl/powsybl-diagram
- **CGMES** : https://www.entsoe.eu/digital/common-information-model/
- **IEC 61850-6** : SCL Language
- **IEC 61970-301** : CIM Base
- **IEC 62361-102** : Harmonization IEC 61850 / CIM

## Valeur pédagogique

Ce projet permet d'apprendre :
- ✅ **IEC 61850** : Standard des postes électriques
- ✅ **CIM/CGMES** : Standard des réseaux de transport
- ✅ **RDF/SPARQL** : Technologies sémantiques
- ✅ **Génération SVG** : Visualisation de données techniques
- ✅ **Intégration d'outils externes** : PowSyBl
- ✅ **Conventions RTE** : Règles métier d'un TSO

C'est un projet complet qui couvre :
- Backend (FastAPI, RDF, SPARQL)
- Frontend (React, SVG)
- Standards industriels (IEC 61850, CIM)
- Outils de production (PowSyBl)
