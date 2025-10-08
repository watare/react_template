# 👋 Lisez-moi d'abord !

## Application Template WebApp - Prête à l'emploi

Cette application est un **template complet** pour développer des applications web modernes avec :

- 🔐 **Authentification JWT**
- 👥 **RBAC** (Role-Based Access Control)
- ⚛️ **React + TypeScript + Vite**
- 🚀 **FastAPI (Python)**
- 🗄️ **PostgreSQL** (données relationnelles)
- 🕸️ **Apache Jena Fuseki** (graphe RDF)
- 🐳 **Docker** (orchestration complète)

---

## 🚀 Démarrage Ultra-Rapide (2 minutes)

```bash
cd template-webapp

# Démarrer TOUT automatiquement
docker-compose up -d

# Suivre les logs (optionnel)
docker-compose logs -f backend
```

**Attendre 60 secondes**, puis ouvrir : **http://localhost:5173**

**Se connecter avec** : `admin` / `admin`

---

## ✅ Vérifier que tout fonctionne

```bash
# Script de test automatique
bash test_setup.sh
```

Vous devriez voir tous les ✓ verts.

---

## 📚 Documentation

Selon ce que vous cherchez :

| Document | Quand l'utiliser |
|----------|------------------|
| **[START.md](START.md)** | Guide complet avec troubleshooting détaillé |
| **[QUICKSTART.md](QUICKSTART.md)** | Démarrage rapide en 2 étapes |
| **[MANUAL_SETUP.md](MANUAL_SETUP.md)** | Si l'auto-init échoue (rare) |
| **[README.md](README.md)** | Documentation technique complète |
| **[FIXES.md](FIXES.md)** | Corrections apportées pour le login |

---

## 🔑 Identifiants par défaut

| Utilisateur | Mot de passe | Rôle | Permissions |
|-------------|--------------|------|-------------|
| **admin** | admin | Admin | Toutes |
| **demo** | demo | Viewer | Lecture seule |

---

## 🌐 Points d'accès

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Interface utilisateur React |
| **API** | http://localhost:8000 | Backend FastAPI |
| **API Docs** | http://localhost:8000/docs | Documentation Swagger interactive |
| **Fuseki** | http://localhost:3030 | Interface SPARQL RDF |

---

## 🧪 Tests rapides

### Test 1 : API Health

```bash
curl http://localhost:8000/health
```

**Attendu** : `{"status":"healthy"}`

### Test 2 : Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

**Attendu** : Un JSON avec `access_token`

### Test 3 : Frontend

Ouvrir http://localhost:5173 dans un navigateur.

**Attendu** : Page de login

---

## 🛠️ Commandes utiles

### Voir les logs

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Redémarrer

```bash
# Un service
docker-compose restart backend

# Tout
docker-compose restart
```

### Réinitialiser complètement

```bash
docker-compose down -v
docker-compose up -d
```

---

## ❌ Problèmes courants

### "Connection refused" au login

**Cause** : Le backend n'est pas encore prêt

**Solution** : Attendre 60 secondes ou vérifier les logs :
```bash
docker-compose logs backend | grep "Application startup complete"
```

### "401 Unauthorized"

**Cause** : Base de données non initialisée

**Solution** :
```bash
# Vérifier que les users existent
docker-compose exec postgres psql -U postgres -d template_db -c "SELECT * FROM users;"

# Si vide, réinitialiser
docker-compose down -v
docker-compose up -d
```

### Services ne démarrent pas

**Solution** :
```bash
# Vérifier l'état
docker-compose ps

# Voir les erreurs
docker-compose logs

# Rebuild
docker-compose up -d --build
```

---

## 🎯 Que faire après ?

1. ✅ **Se connecter** au frontend
2. 📊 **Explorer le dashboard** (statistiques)
3. 🕸️ **Créer un nœud RDF** (page Nodes)
4. 🔍 **Tester SPARQL** sur Fuseki
5. 📖 **Lire l'API Docs** interactive
6. 🎨 **Personnaliser** pour votre cas d'usage

---

## 🏗️ Architecture

```
Frontend (React)  →  Backend (FastAPI)  →  PostgreSQL (Users, RBAC)
                                        →  Fuseki (RDF Graph)
```

- **PostgreSQL** : Utilisateurs, rôles, permissions, audit
- **Fuseki** : Données métier sous forme de graphe RDF
- **Backend** : API REST avec authentification JWT
- **Frontend** : Interface React moderne

---

## 📦 Ce qui est inclus

✅ **Authentification complète** (register, login, JWT)
✅ **RBAC** (3 rôles, 7 permissions)
✅ **CRUD RDF** via SPARQL
✅ **Audit logging** de toutes les actions
✅ **Dashboard** avec statistiques
✅ **Interface moderne** et responsive
✅ **Docker Compose** pour tout orchestrer
✅ **Scripts d'initialisation** automatiques
✅ **Documentation complète**

---

## 💡 Besoin d'aide ?

1. Consultez [START.md](START.md) pour le guide complet
2. Lisez [FIXES.md](FIXES.md) pour comprendre les corrections
3. Testez avec `bash test_setup.sh`
4. Vérifiez les logs : `docker-compose logs`

---

**Bon développement ! 🚀**
