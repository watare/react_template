# Template WebApp - Full Stack Application

Application web template complète avec authentification, RBAC, React + Vite, FastAPI, PostgreSQL et Apache Jena Fuseki (RDF).

## 🎯 Architecture

Cette application démontre une architecture moderne full-stack avec conversion automatique SCL-to-RDF :

```
┌─────────────────────────────────────────────┐
│  Frontend (React + Vite + TypeScript)       │
│  - Authentification JWT                     │
│  - React Query pour state management        │
│  - Upload SCL avec drag-and-drop            │
│  - Visualisation RDF interactive            │
└────────────────┬────────────────────────────┘
                 │ HTTP/REST
                 ↓
┌─────────────────────────────────────────────┐
│  Backend (FastAPI + Python)                 │
│  - API REST                                 │
│  - Authentification JWT                     │
│  - RBAC (Roles & Permissions)               │
│  - Conversion SCL ↔ RDF (iec61850)          │
│  - Validation round-trip                    │
│  - Background processing                    │
└───────┬─────────────────┬───────────────────┘
        │                 │
        ↓                 ↓
┌───────────────┐  ┌────────────────────────┐
│  PostgreSQL   │  │  Apache Jena Fuseki    │
│  - Users      │  │  - RDF Triple Store    │
│  - Roles      │  │  - SPARQL endpoint     │
│  - SCL files  │  │  - Per-file datasets   │
│  - Audit logs │  │  - Graph queries       │
└───────────────┘  └────────────────────────┘
```

## 🚀 Démarrage rapide

### Prérequis

- Docker & Docker Compose
- Git

### Installation

1. **Cloner le projet**
   ```bash
   git clone <url>
   cd template-webapp
   ```

2. **Créer le fichier .env**
   ```bash
   cp .env.example .env
   ```

3. **Démarrer les services**
   ```bash
   docker-compose up -d
   ```

   **Que se passe-t-il automatiquement ?**
   - ✅ PostgreSQL démarre et crée les bases de données
   - ✅ Fuseki démarre et crée le dataset par défaut
   - ✅ Backend exécute les migrations automatiquement (`init_db.py`)
   - ✅ Création des utilisateurs et rôles par défaut
   - ✅ Initialisation du dataset RDF (`init_rdf.py`)
   - ✅ FastAPI démarre sur le port 8000
   - ✅ Frontend (React) démarre sur le port 5173

4. **Vérifier que tout est démarré** (optionnel)
   ```bash
   docker-compose logs -f backend
   # Attendre le message : "Started FastAPI server" (~30 secondes)
   ```

5. **Accéder à l'application**
   - **Frontend**: http://localhost:5173
   - **API Backend**: http://localhost:8000
   - **Documentation API**: http://localhost:8000/docs
   - **Fuseki UI**: http://localhost:3030

### Identifiants par défaut

- **Admin**: `admin` / `admin123`
- **Demo (lecture seule)**: `demo` / `demo123`

### ⚠️ Aucune migration manuelle nécessaire !

Tout est automatisé dans `docker-compose.yml` :
```yaml
backend:
  command: >
    sh -c "
      bash scripts/wait_for_services.sh &&
      python scripts/init_db.py &&        # ← Migrations PostgreSQL
      python scripts/init_rdf.py &&       # ← Dataset Fuseki
      uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    "
```

## 📁 Structure du projet

```
template-webapp/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/               # Routes API
│   │   │   ├── auth.py        # Authentification
│   │   │   ├── nodes.py       # Gestion des nœuds RDF
│   │   │   └── scl_files.py   # Upload & conversion SCL (NOUVEAU)
│   │   ├── auth/              # Système d'authentification
│   │   │   └── dependencies.py # Dépendances auth & RBAC
│   │   ├── core/              # Configuration
│   │   │   ├── config.py      # Settings
│   │   │   └── security.py    # JWT & hashing
│   │   ├── db/                # Base de données
│   │   │   └── base.py        # SQLAlchemy setup
│   │   ├── models/            # Modèles SQLAlchemy
│   │   │   ├── user.py        # User, Role, Permission, AuditLog
│   │   │   └── scl_file.py    # SCLFile (NOUVEAU)
│   │   ├── rdf/               # Client RDF
│   │   │   ├── client.py      # Client Fuseki (étendu)
│   │   │   └── queries.py     # Templates SPARQL
│   │   ├── scl_converter.py   # Convertisseur SCL ↔ RDF (NOUVEAU)
│   │   └── main.py            # Point d'entrée FastAPI
│   ├── alembic/               # Migrations base de données
│   │   └── versions/
│   │       ├── 001_*.py       # Users, roles, permissions
│   │       └── 002_*.py       # SCL files table (NOUVEAU)
│   ├── scripts/               # Scripts d'initialisation
│   │   ├── init_db.py         # Initialise PostgreSQL + migrations
│   │   ├── init_rdf.py        # Initialise Fuseki
│   │   └── setup.sh           # Script complet
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── components/        # Composants React
│   │   │   └── Layout.tsx     # Layout principal (navigation)
│   │   ├── hooks/             # Custom hooks
│   │   │   ├── useAuth.ts     # Hook authentification
│   │   │   ├── useNodes.ts    # Hook gestion RDF
│   │   │   └── useSCLFiles.ts # Hook SCL files (NOUVEAU)
│   │   ├── pages/             # Pages
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx      # Dashboard avec upload (NOUVEAU)
│   │   │   ├── NodesPage.tsx
│   │   │   ├── SCLFilesPage.tsx       # Galerie fichiers (NOUVEAU)
│   │   │   └── RDFSchemaPage.tsx      # Visualisation RDF (NOUVEAU)
│   │   ├── services/          # Services API
│   │   │   └── api.ts         # Axios client
│   │   ├── types/             # Types TypeScript
│   │   │   └── index.ts       # User, SCLFile, Node
│   │   ├── styles/            # Styles CSS
│   │   │   └── index.css
│   │   ├── App.tsx            # Composant principal + routes
│   │   └── main.tsx           # Point d'entrée
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
│
├── docker-compose.yml          # Orchestration services
├── .env.example               # Variables d'environnement
├── SCL_FILES_FEATURE.md       # Documentation SCL feature (NOUVEAU)
└── README.md                  # Ce fichier
```

## 🔐 Système RBAC

### Rôles par défaut

- **Admin**: Tous les droits
- **Editor**: Lecture et écriture (pas de suppression)
- **Viewer**: Lecture seule

### Permissions

- `nodes:read`: Lire les nœuds RDF
- `nodes:write`: Créer/modifier les nœuds RDF
- `nodes:delete`: Supprimer les nœuds RDF
- `users:read`: Lire les utilisateurs
- `users:write`: Créer/modifier les utilisateurs
- `users:delete`: Supprimer les utilisateurs
- `admin`: Accès administrateur complet

## 🗄️ Base de données

### PostgreSQL

Utilisé pour :
- Gestion des utilisateurs
- Système de rôles et permissions (RBAC)
- Journalisation des audits (qui a fait quoi, quand)

### Apache Jena Fuseki (RDF)

Utilisé pour :
- Stockage de données fortement interconnectées
- Requêtes SPARQL sur des graphes
- Données métier complexes et évolutives

**Exemple de requête SPARQL** :
```sparql
PREFIX vocab: <http://template.app/vocab#>

SELECT ?device ?status
WHERE {
  ?device a vocab:Device ;
          vocab:status ?status .
}
```

## 🔧 API Endpoints

### Authentification

- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter
- `GET /api/auth/me` - Informations utilisateur actuel

### Nœuds RDF

- `GET /api/nodes/` - Liste tous les nœuds
- `GET /api/nodes/{id}` - Détails d'un nœud
- `POST /api/nodes/` - Créer un nœud
- `PATCH /api/nodes/{id}` - Modifier un nœud
- `DELETE /api/nodes/{id}` - Supprimer un nœud
- `GET /api/nodes/search?q=term` - Rechercher
- `GET /api/nodes/stats` - Statistiques

### 🆕 Fichiers SCL (Admin uniquement)

- `POST /api/scl-files/upload` - Upload fichier SCL (.scd, .icd, .cid)
  - Max 100MB
  - Conversion automatique vers RDF
  - Validation round-trip
- `GET /api/scl-files/` - Liste tous les fichiers
- `GET /api/scl-files/{id}` - Détails d'un fichier
- `GET /api/scl-files/{id}/rdf-schema` - Analyse du schéma RDF
  - Classes RDF trouvées
  - Exemples de triples
  - Namespaces utilisés
- `DELETE /api/scl-files/{id}` - Supprimer fichier + dataset RDF

## 🆕 Feature: Conversion SCL vers RDF

### Workflow Automatique

1. **Upload** (Admin Dashboard ou page dédiée)
   - Drag-and-drop ou sélection de fichier
   - Validation: extension (.scd, .icd, .cid) et taille (max 100MB)
   - Upload vers backend

2. **Conversion** (Background automatique)
   ```
   SCL (XML) → RDF (Turtle)
   ```
   - Préservation complète de la structure XML
   - URIs uniques pour chaque élément IEC 61850
   - Stockage dans Fuseki dataset dédié (`scl_file_{id}`)

3. **Validation** (Round-trip)
   ```
   RDF → SCL (XML)
   ```
   - Régénération du fichier SCL depuis RDF
   - Comparaison byte-level + XML sémantique
   - Résultat: ✓ Validated ou ✗ Failed

4. **Visualisation**
   - Exploration interactive du schéma RDF
   - Browse par classe (IED, LNode, Substation, etc.)
   - Exemples de triples pour chaque type
   - Templates SPARQL prêts à l'emploi

### Dashboard Admin

Le dashboard affiche pour les admins :

**📤 Upload SCL File**
- Bouton "Choose File" pour upload rapide
- Lien vers la galerie complète

**📁 Recent SCL Files**
- 5 fichiers les plus récents
- Status badges (uploaded → converting → validated)
- Taille fichier + nombre de triples
- Clic pour voir le schéma RDF (si validated)

**Quick Actions**
- Lien "SCL Files" vers la galerie complète

### Page Galerie (`/scl-files`)

**Vue en grille** :
- Cards pour chaque fichier
- Status coloré (bleu=uploaded, jaune=converting, vert=validated, rouge=failed)
- Badge de validation (✓/✗)
- Métadonnées (uploader, date, taille, triples)
- Actions: "View RDF Schema" ou "Delete"

**Upload zone** :
- Drag-and-drop
- Validation côté client
- Feedback temps réel

### Page Visualisation RDF (`/scl-files/{id}/rdf-schema`)

**Sidebar** : Liste des classes RDF
- Nom de classe (ex: IED, LNode, Substation)
- Nombre d'instances

**Panel principal** :
- Détails de la classe sélectionnée
- Exemples de triples (subject → predicate → object)
- Accordion expandable
- Template SPARQL pré-rempli
- Lien vers Fuseki UI pour requêtes avancées

**Section Namespaces** :
- Tous les namespaces utilisés dans le graph

### Base de Données

**PostgreSQL** : Table `scl_files`
```sql
scl_files (
  id,                    -- PK
  filename,              -- Nom unique (timestamp + filename)
  original_filename,     -- Nom original
  file_size,             -- Taille en bytes
  scl_path,              -- Chemin fichier SCL original
  rdf_path,              -- Chemin fichier RDF généré
  validated_scl_path,    -- Chemin fichier SCL régénéré
  status,                -- uploaded|converting|converted|validated|failed
  is_validated,          -- Boolean
  validation_passed,     -- Boolean (true si round-trip OK)
  validation_message,    -- Message de validation
  triple_count,          -- Nombre de triples RDF
  fuseki_dataset,        -- Nom du dataset Fuseki (scl_file_{id})
  uploaded_by,           -- FK vers users(id)
  uploaded_at,           -- Timestamp
  converted_at           -- Timestamp
)
```

**Fuseki** : Un dataset par fichier
- Dataset: `scl_file_1`, `scl_file_2`, etc.
- Isolation des données
- SPARQL queries par fichier
- Suppression facile (drop dataset)

### Requêtes SPARQL Utilisées

**1. Classes et comptage**
```sparql
SELECT ?type (COUNT(?s) AS ?count)
WHERE {
  ?s rdf:type ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
```

**2. Exemples de triples par classe**
```sparql
SELECT ?s ?p ?o
WHERE {
  ?s rdf:type <http://iec61850.com/SCL#IED> .
  ?s ?p ?o .
}
LIMIT 10
```

**3. Extraction des namespaces**
```sparql
SELECT DISTINCT ?ns
WHERE {
  { SELECT DISTINCT (STRBEFORE(STR(?s), "#") AS ?ns) WHERE { ?s ?p ?o } }
  UNION
  { SELECT DISTINCT (STRBEFORE(STR(?p), "#") AS ?ns) WHERE { ?s ?p ?o } }
}
```

### Documentation Complète

Voir `SCL_FILES_FEATURE.md` pour :
- Architecture détaillée
- Data flow (PostgreSQL vs Fuseki vs Filesystem vs Component state)
- Décisions de design (pourquoi pas de Redux)
- Sécurité et access control
- Troubleshooting

## 🛠️ Développement

### Backend

```bash
# Accéder au container
docker-compose exec backend bash

# Exécuter les tests
pytest

# Accéder au shell Python
python
```

### Frontend

```bash
# Accéder au container
docker-compose exec frontend sh

# Installer une dépendance
npm install <package>

# Rebuild
npm run build
```

### Logs

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f fuseki
```

## 📊 Fuseki - Interface RDF

### Accès

http://localhost:3030

### Dataset

- **Nom**: `template_dataset`
- **Type**: TDB2 (persistant)

### Exemples de requêtes

**Lister tous les nœuds** :
```sparql
SELECT ?s ?p ?o
WHERE {
  ?s ?p ?o .
}
LIMIT 100
```

**Compter les triplets** :
```sparql
SELECT (COUNT(*) AS ?count)
WHERE {
  ?s ?p ?o .
}
```

## 🔄 Commandes utiles

### Redémarrer les services

```bash
docker-compose restart
```

### Réinitialiser les données

```bash
# Arrêter et supprimer les volumes
docker-compose down -v

# Redémarrer
docker-compose up -d

# Réinitialiser
docker-compose exec backend bash scripts/setup.sh
```

### Sauvegarder les données RDF

```bash
curl -X GET "http://localhost:3030/template_dataset/data" \
  -H "Accept: application/n-triples" \
  > backup.nt
```

### Restaurer les données RDF

```bash
curl -X POST "http://localhost:3030/template_dataset/data" \
  -H "Content-Type: application/n-triples" \
  --data-binary @backup.nt
```

## 🎨 Frontend

### Technologies

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool ultra-rapide
- **React Router** - Navigation
- **React Query** - State management & caching
- **Axios** - HTTP client

### Fonctionnalités

- ✅ Authentification JWT
- ✅ Routes protégées
- ✅ Gestion de l'état avec React Query
- ✅ Interface responsive
- ✅ Gestion des erreurs
- ✅ Cache automatique des requêtes

## 🔒 Sécurité

- **JWT tokens** pour l'authentification
- **Bcrypt** pour le hashing des mots de passe
- **RBAC** pour les autorisations
- **CORS** configuré
- **Audit logging** de toutes les actions
- **Variables d'environnement** pour les secrets

## 📝 Variables d'environnement

Voir `.env.example` pour la liste complète.

**Importantes** :
- `SECRET_KEY` - Clé pour JWT (CHANGER EN PRODUCTION!)
- `POSTGRES_PASSWORD` - Mot de passe PostgreSQL
- `FUSEKI_ADMIN_PASSWORD` - Mot de passe admin Fuseki

## 🚢 Déploiement en production

1. **Modifier `.env`** :
   - Générer une nouvelle `SECRET_KEY`
   - Changer tous les mots de passe
   - Désactiver `DEBUG=False`

2. **Build de production** :
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Sécuriser** :
   - Utiliser HTTPS (nginx + Let's Encrypt)
   - Configurer un firewall
   - Limiter l'accès à Fuseki UI

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/)
- [SPARQL Tutorial](https://www.w3.org/TR/sparql11-query/)
- [PostgreSQL](https://www.postgresql.org/docs/)

## 🤝 Support

Pour toute question, consultez :
- Documentation API : http://localhost:8000/docs
- Guide RDF : `/docs/09-rdf-guide.md`

## 📄 Licence

MIT
