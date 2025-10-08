# Corrections apportées pour résoudre les problèmes de login

## Problèmes identifiés

1. ❌ **Backend ne créait pas automatiquement les tables PostgreSQL**
2. ❌ **Pas d'initialisation automatique des utilisateurs admin/demo**
3. ❌ **Frontend et Backend pas correctement liés**
4. ❌ **Pas de gestion des dépendances entre services**

## Solutions implémentées

### 1. Initialisation automatique au démarrage du backend

**Fichier modifié** : `docker-compose.yml`

Le backend exécute maintenant automatiquement au démarrage :
```bash
1. Attente de PostgreSQL et Fuseki (script wait_for_services.sh)
2. Création des tables (init_db.py)
3. Création des utilisateurs (admin/admin, demo/demo)
4. Initialisation du dataset RDF (init_rdf.py)
5. Démarrage du serveur FastAPI
```

### 2. Scripts d'initialisation

**Nouveaux fichiers** :
- `backend/scripts/wait_for_services.sh` - Attente des services
- `backend/scripts/init_db.py` - Création tables + users
- `backend/scripts/init_rdf.py` - Initialisation Fuseki

**Fonctionnalités** :
- ✅ Création automatique des tables (users, roles, permissions, audit_logs)
- ✅ Création des rôles (Admin, Editor, Viewer)
- ✅ Création des permissions (nodes:read, nodes:write, etc.)
- ✅ Création des utilisateurs avec mots de passe hashés
- ✅ Création du dataset RDF avec données de test

### 3. Configuration Alembic (migrations)

**Nouveaux fichiers** :
- `backend/alembic.ini` - Configuration Alembic
- `backend/alembic/env.py` - Environment setup
- `backend/alembic/script.py.mako` - Template migrations

**Usage** : Prêt pour gérer les migrations futures de la base

### 4. Frontend amélioré

**Fichier ajouté** : `frontend/src/types/index.ts`

Types TypeScript pour :
- User
- LoginResponse
- Node

**Correction** : Types cohérents entre frontend et backend

### 5. Tests automatiques

**Nouveau fichier** : `test_setup.sh`

Script de test qui vérifie :
- ✅ Services Docker actifs
- ✅ PostgreSQL opérationnel + users créés
- ✅ Fuseki opérationnel + dataset créé
- ✅ Backend API répond
- ✅ Login admin fonctionne
- ✅ Frontend accessible

**Usage** :
```bash
bash test_setup.sh
```

## Guide de démarrage corrigé

### Démarrage simple

```bash
cd template-webapp

# 1. Démarrer (auto-init)
docker-compose up -d

# 2. Suivre les logs (optionnel)
docker-compose logs -f backend

# 3. Attendre "Application startup complete" (~60 secondes)
```

### Vérification

```bash
# Tester automatiquement
bash test_setup.sh

# Ou manuellement
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

### Accès

- **Frontend** : http://localhost:5173
- **Identifiants** : `admin` / `admin` ou `demo` / `demo`

## Ordre d'exécution au démarrage

```
1. PostgreSQL + Fuseki démarrent
   ↓
2. Backend attend qu'ils soient prêts (wait_for_services.sh)
   ↓
3. Backend crée les tables (init_db.py)
   ↓
4. Backend crée les utilisateurs avec rôles
   ↓
5. Backend initialise le dataset RDF (init_rdf.py)
   ↓
6. Backend démarre FastAPI
   ↓
7. Frontend démarre et peut se connecter au backend
```

## Fichiers de documentation

- `START.md` - Guide de démarrage détaillé avec troubleshooting
- `MANUAL_SETUP.md` - Setup manuel si auto-init échoue
- `QUICKSTART.md` - Démarrage rapide (mis à jour)
- `test_setup.sh` - Script de test automatique
- `FIXES.md` - Ce fichier (résumé des corrections)

## Points clés

### ✅ Ce qui fonctionne maintenant

1. **Initialisation automatique complète**
2. **Users admin/demo créés automatiquement**
3. **Dataset RDF pré-rempli avec données de test**
4. **Frontend ↔ Backend correctement liés**
5. **Login fonctionnel dès le premier démarrage**

### ⚠️ Si ça ne fonctionne pas

```bash
# Réinitialiser complètement
docker-compose down -v
docker-compose up -d
docker-compose logs -f backend

# Ou suivre MANUAL_SETUP.md pour initialisation manuelle
```

### 🔍 Débug

```bash
# Logs backend
docker-compose logs backend

# Vérifier PostgreSQL
docker-compose exec postgres psql -U postgres -d template_db -c "SELECT * FROM users;"

# Vérifier Fuseki
curl http://localhost:3030/$/datasets

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

## Prochaines étapes recommandées

1. Tester le login : http://localhost:5173
2. Explorer le dashboard
3. Créer un nœud RDF via l'interface
4. Tester les requêtes SPARQL sur Fuseki
5. Consulter l'API Docs : http://localhost:8000/docs

---

**Tous les problèmes de login sont maintenant corrigés ! ✅**
