# Project: Learning Web Development with AI

## Project Goal
This is a learning project to understand modern web development with:
- React + TypeScript (Frontend)
- FastAPI + Python (Backend)
- PostgreSQL (Relational Database)
- Apache Jena Fuseki (RDF Triplestore)
- RBAC (Role-Based Access Control)

## Learning Approach
- **Step-by-step progression** - understand each layer before adding the next
- **Explanation-first** - explain concepts before implementing
- **Document everything** - maintain BOOK.md as learning handbook
- **Question-driven** - ask "why" at each decision point

## Development Instructions
- Explain each step and technology choice
- Update BOOK.md with learnings as we progress
- Build incrementally: React → FastAPI → PostgreSQL → Auth/RBAC → RDF
- Use Docker Compose for service orchestration
- Focus on understanding over speed

## Deployment
- VPS: ubuntu@141.94.244.15 (SSH: ~/.ssh/ovh_rsa)
- Deploy only when explicitly requested
- Document deployment steps in BOOK.md

## Documentation
- **BOOK.md** - Main learning handbook (concepts, decisions, how-to)
- **JIRA/Confluence** - Track tasks and decisions (VPAC space)
- Atomic commits linked to JIRA tickets

## Current Phase
Phase 1: React Frontend (standalone with mock data)
- c'est un projet local pour apprendre on reste en localhost

## Technical Architecture

### Infrastructure (Docker)
**TOUT EST DOCKERISÉ** - Ne jamais essayer d'installer npm localement
- **Frontend**: Container React + Vite (port 5173) avec hot-reload
- **Backend**: Container FastAPI + Python (port 8000) avec auto-reload
- **PostgreSQL**: Container Postgres 15 (port 5432)
- **Fuseki**: Container Apache Jena (port 3030) - RDF triplestore

Volumes importants:
- `/app/node_modules` - Monté dans container frontend (NE PAS TOUCHER)
- `./frontend:/app` - Code source frontend synchronisé
- `./backend:/app` - Code source backend synchronisé

### SLD (Single Line Diagram) Architecture

#### 1. Data Flow: SCL → RDF → SLD
```
SCL File (IEC 61850)
  → Parse & Convert (scl_converter.py)
  → RDF Triples (Fuseki)
  → SPARQL Queries (sld_queries.py)
  → Component Data (JSON)
  → React Components (SLDCanvas, VoltageLevel, Bay, Equipment)
```

#### 2. Component Architecture
- **SLDCanvas**: Canvas principal avec pan/zoom, gère l'état global
- **VoltageLevel**: Représente un niveau de tension (jeu de barres)
- **Bay**: Travée (colonne verticale d'équipements)
- **Equipment**: Équipement individuel avec symbole QElectroTech

#### 3. Symbol System (QElectroTech)
**Symboles professionnels IEC 61850** depuis backend:
- Fichiers SVG: `/backend/app/sld/symbols/svg/*.svg`
- Métadonnées: `/backend/app/sld/symbols/svg/symbols_library.json`
- API endpoints:
  - `GET /api/sld/symbols` - Liste des symboles disponibles
  - `GET /api/sld/symbols/{type}` - SVG d'un symbole (CBR, DIS, CTR, VTR, PTR)
- Frontend: Equipment.tsx charge les symboles via API (fallback sur symboles basiques)

#### 4. Layout Rules (RTE Conventions)
Fichier: `/backend/app/sld/rte_rules.py`
- Convention française (RTE) pour disposition des équipements
- Ordre vertical: Busbar → DIS_SA → DIS_SL → CBR → DIS_ST → CTR/VTR
- Support multi-niveaux de tension empilés verticalement
- Gestion couplage de barres (CBO) sur les côtés
- **TODO**: Règles spécifiques TC/TT/VT pour lisibilité

Fichiers RTE pour pays différents possibles (ex: `elia_rules.py` pour Belgique)

#### 5. RDF Schema for Diagram Layout (TODO)
**Architecture cible** - Persister les positions graphiques en RDF:

```turtle
@prefix dl: <http://iec.ch/TC57/CIM100#> .
@prefix iec: <http://iec.ch/TC57/2013/CIM-schema-cim16#> .

# DiagramObject (lien Equipment → Position)
:DiagramObject_CBR001 a dl:DiagramObject ;
    dl:IdentifiedObject.name "CBR001" ;
    dl:DiagramObject.IdentifiedObject :CBR001 ;  # Link to IEC 61850 equipment
    dl:DiagramObject.DiagramObjectPoints (
        :Point_CBR001_1
        :Point_CBR001_2
    ) ;
    dl:DiagramObject.rotation "0.0"^^xsd:float .

# DiagramObjectPoint (positions vectorielles)
:Point_CBR001_1 a dl:DiagramObjectPoint ;
    dl:DiagramObjectPoint.xPosition "150.0"^^xsd:float ;
    dl:DiagramObjectPoint.yPosition "200.0"^^xsd:float ;
    dl:DiagramObjectPoint.sequenceNumber "1"^^xsd:int .
```

**Avantages**:
- Positions persistées dans RDF (modification possible)
- Génération SLD depuis CIM si besoin (avant SCL chargé)
- Support création manuelle de schémas
- Robuste aux modifications de position (sauvegarde/restauration)

#### 6. API Endpoints
- `POST /api/sld/generate-data` - Génère données structurées pour rendu component-based
- `POST /api/sld/generate-simple` - Génère SVG simple (POC, deprecated)
- `GET /api/sld/symbols` - Liste symboles QElectroTech
- `GET /api/sld/symbols/{type}` - SVG d'un symbole