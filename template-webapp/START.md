# 🚀 Guide de Démarrage - TESTÉ

## Démarrage Automatique (Recommandé)

```bash
cd template-webapp

# 1. Démarrer tous les services (auto-initialisation)
docker-compose up -d

# 2. Suivre les logs pour voir la progression
docker-compose logs -f backend
```

**Ce qui se passe automatiquement** :
1. ✅ PostgreSQL démarre et crée la base de données
2. ✅ Fuseki démarre et crée le dataset RDF
3. ✅ Le backend attend que les services soient prêts
4. ✅ Les tables PostgreSQL sont créées
5. ✅ Les utilisateurs admin/demo sont créés
6. ✅ Les données RDF de test sont chargées
7. ✅ Le serveur FastAPI démarre
8. ✅ Le frontend React démarre

**Durée totale** : ~30-60 secondes

---

## Vérification

### 1. Vérifier que tous les services sont UP

```bash
docker-compose ps
```

Vous devriez voir :
```
NAME                 STATUS
template_backend     Up
template_frontend    Up
template_fuseki      Up
template_postgres    Up (healthy)
```

### 2. Tester l'API

```bash
# Health check
curl http://localhost:8000/health

# Devrait retourner: {"status":"healthy"}
```

### 3. Se connecter au frontend

Ouvrir : **http://localhost:5173**

**Identifiants de test** :
- **Admin** : `admin` / `admin`
- **Demo** : `demo` / `demo`

---

## En cas de problème

### Logs backend ne montrent pas l'initialisation

```bash
# Vérifier les logs
docker-compose logs backend

# Si bloqué, redémarrer
docker-compose restart backend
docker-compose logs -f backend
```

### Erreur "Connection refused" au login

**Cause** : Le backend n'est pas encore prêt

**Solution** :
```bash
# Attendre que le backend soit complètement démarré
docker-compose logs -f backend | grep "Application startup complete"

# Une fois ce message affiché, rafraîchir le frontend
```

### Base de données vide

```bash
# Réinitialiser complètement
docker-compose down -v
docker-compose up -d
docker-compose logs -f backend
```

### Erreur CORS

Vérifier `.env` :
```bash
CORS_ORIGINS=http://localhost:5173
VITE_API_URL=http://localhost:8000
```

---

## Accès aux services

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Frontend** | http://localhost:5173 | admin/admin ou demo/demo |
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Fuseki UI** | http://localhost:3030 | admin/admin |
| **PostgreSQL** | localhost:5432 | postgres/postgres |

---

## Commandes utiles

### Redémarrer un service

```bash
docker-compose restart backend
docker-compose restart frontend
```

### Voir les logs en temps réel

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Accéder à un container

```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# PostgreSQL
docker-compose exec postgres psql -U postgres -d template_db
```

### Réinitialiser complètement

```bash
# Arrêter et supprimer volumes
docker-compose down -v

# Redémarrer
docker-compose up -d

# Suivre les logs
docker-compose logs -f backend
```

---

## Tests rapides

### 1. Tester le login via API

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

**Attendu** : Un JSON avec `access_token`

### 2. Vérifier PostgreSQL

```bash
docker-compose exec postgres psql -U postgres -d template_db -c "SELECT username FROM users;"
```

**Attendu** :
```
 username
----------
 admin
 demo
```

### 3. Vérifier Fuseki

```bash
curl -X POST http://localhost:3030/template_dataset/sparql \
  -H "Content-Type: application/sparql-query" \
  -d "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
```

**Attendu** : Un JSON avec le nombre de triplets (devrait être > 0)

---

## Troubleshooting détaillé

### Le backend ne démarre pas

```bash
# Voir les logs d'erreur
docker-compose logs backend

# Problèmes courants:
# - PostgreSQL pas prêt → attendre 10s de plus
# - Erreur de syntaxe Python → vérifier les fichiers .py
# - Port 8000 occupé → changer BACKEND_PORT dans .env
```

### Le frontend ne trouve pas le backend

1. Vérifier que le backend est up :
   ```bash
   curl http://localhost:8000/health
   ```

2. Vérifier la config frontend :
   ```bash
   docker-compose exec frontend sh -c 'echo $VITE_API_URL'
   # Devrait afficher: http://localhost:8000
   ```

3. Rebuild le frontend :
   ```bash
   docker-compose restart frontend
   ```

### Login échoue avec "401 Unauthorized"

**Possibles causes** :

1. **Base de données non initialisée**
   ```bash
   # Vérifier que les users existent
   docker-compose exec postgres psql -U postgres -d template_db -c "SELECT * FROM users;"
   ```

2. **Mauvais mot de passe**
   - Assurez-vous d'utiliser `admin` / `admin`

3. **Backend pas en mode DEBUG**
   - Vérifier `.env` : `DEBUG=True`

---

## Architecture des services

```
┌─────────────────┐
│   Frontend      │  Port 5173
│   (React)       │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│   Backend       │  Port 8000
│   (FastAPI)     │
└────┬───────┬────┘
     │       │
     ↓       ↓
┌─────────┐ ┌──────────┐
│PostgreSQL Port 5432
│         │ │  Fuseki  │  Port 3030
│ Users   │ │   RDF    │
│ RBAC    │ │  Graph   │
└─────────┘ └──────────┘
```

---

## Next Steps

Une fois connecté :

1. **Dashboard** : Voir les statistiques
2. **Nodes** : Créer votre premier nœud RDF
3. **Fuseki UI** : Explorer les données avec SPARQL
4. **API Docs** : Tester l'API interactivement

---

**Questions ?** Consultez le [README.md](README.md) complet
