# Template WebApp - Full Stack Application

Application web template complète avec authentification, RBAC, React + Vite, FastAPI, PostgreSQL et Apache Jena Fuseki (RDF).

## 🎯 Architecture

Cette application démontre une architecture moderne full-stack :

```
┌─────────────────────────────────────────────┐
│  Frontend (React + Vite + TypeScript)       │
│  - Authentification JWT                     │
│  - React Query pour state management        │
│  - Interface moderne et responsive          │
└────────────────┬────────────────────────────┘
                 │ HTTP/REST
                 ↓
┌─────────────────────────────────────────────┐
│  Backend (FastAPI + Python)                 │
│  - API REST                                 │
│  - Authentification JWT                     │
│  - RBAC (Roles & Permissions)               │
│  - Audit logging                            │
└───────┬─────────────────┬───────────────────┘
        │                 │
        ↓                 ↓
┌───────────────┐  ┌────────────────────────┐
│  PostgreSQL   │  │  Apache Jena Fuseki    │
│  - Users      │  │  - RDF Triple Store    │
│  - Roles      │  │  - SPARQL endpoint     │
│  - Permissions│  │  - Graph database      │
│  - Audit logs │  │                        │
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

4. **Initialiser les bases de données**
   ```bash
   # Attendre que tous les services soient démarrés (30 secondes)
   sleep 30

   # Exécuter le script de setup
   docker-compose exec backend bash scripts/setup.sh
   ```

5. **Accéder à l'application**
   - **Frontend**: http://localhost:5173
   - **API Backend**: http://localhost:8000
   - **Documentation API**: http://localhost:8000/docs
   - **Fuseki UI**: http://localhost:3030

### Identifiants par défaut

- **Admin**: `admin` / `admin`
- **Demo (lecture seule)**: `demo` / `demo`

## 📁 Structure du projet

```
template-webapp/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/               # Routes API
│   │   │   ├── auth.py        # Authentification
│   │   │   └── nodes.py       # Gestion des nœuds RDF
│   │   ├── auth/              # Système d'authentification
│   │   │   └── dependencies.py # Dépendances auth & RBAC
│   │   ├── core/              # Configuration
│   │   │   ├── config.py      # Settings
│   │   │   └── security.py    # JWT & hashing
│   │   ├── db/                # Base de données
│   │   │   └── base.py        # SQLAlchemy setup
│   │   ├── models/            # Modèles SQLAlchemy
│   │   │   └── user.py        # User, Role, Permission, AuditLog
│   │   ├── rdf/               # Client RDF
│   │   │   ├── client.py      # Client Fuseki
│   │   │   └── queries.py     # Templates SPARQL
│   │   └── main.py            # Point d'entrée FastAPI
│   ├── scripts/               # Scripts d'initialisation
│   │   ├── init_db.py         # Initialise PostgreSQL
│   │   ├── init_rdf.py        # Initialise Fuseki
│   │   └── setup.sh           # Script complet
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── components/        # Composants React
│   │   │   └── Layout.tsx     # Layout principal
│   │   ├── hooks/             # Custom hooks
│   │   │   ├── useAuth.ts     # Hook authentification
│   │   │   └── useNodes.ts    # Hook gestion RDF
│   │   ├── pages/             # Pages
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   └── NodesPage.tsx
│   │   ├── services/          # Services API
│   │   │   └── api.ts         # Axios client
│   │   ├── styles/            # Styles CSS
│   │   │   └── index.css
│   │   ├── App.tsx            # Composant principal
│   │   └── main.tsx           # Point d'entrée
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
│
├── docker-compose.yml          # Orchestration services
├── .env.example               # Variables d'environnement
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
