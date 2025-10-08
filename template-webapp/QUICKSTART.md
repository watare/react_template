# 🚀 Guide de démarrage rapide

## Démarrage en 2 étapes

### 1. Lancer Docker Compose

```bash
cd template-webapp
docker-compose up -d
```

**L'initialisation est automatique !** Le backend va :
- ✅ Attendre que PostgreSQL et Fuseki soient prêts
- ✅ Créer les tables dans PostgreSQL
- ✅ Créer les utilisateurs admin et demo
- ✅ Initialiser le dataset RDF dans Fuseki
- ✅ Démarrer le serveur API

### 2. Suivre les logs

```bash
# Voir la progression de l'initialisation
docker-compose logs -f backend

# Attendre le message "Application startup complete"
```

## ✅ C'est prêt !

Ouvrez votre navigateur : **http://localhost:5173**

Connectez-vous avec :
- **Username**: `admin`
- **Password**: `admin`

---

## 📍 Points d'accès

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Interface utilisateur |
| **API** | http://localhost:8000 | Backend FastAPI |
| **API Docs** | http://localhost:8000/docs | Documentation interactive Swagger |
| **Fuseki** | http://localhost:3030 | Interface RDF SPARQL |

---

## 🔍 Tester l'application

### 1. Créer un nœud RDF

Dans l'interface :
1. Aller sur "Nodes"
2. Cliquer "Create Node"
3. Remplir :
   - ID: `mynode1`
   - Type: `Device`
   - Label: `My First Device`
4. Cliquer "Create Node"

### 2. Requêter avec SPARQL

Aller sur http://localhost:3030 et exécuter :

```sparql
SELECT ?s ?p ?o
WHERE {
  ?s ?p ?o .
}
LIMIT 100
```

### 3. Tester l'API

```bash
# Se connecter
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"

# Copier le token et l'utiliser
curl -X GET "http://localhost:8000/api/nodes/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🛑 Arrêter l'application

```bash
docker-compose down
```

Pour supprimer aussi les données :
```bash
docker-compose down -v
```

---

## 🐛 Problèmes courants

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Redémarrer
docker-compose restart
```

### Erreur "Permission denied" sur setup.sh

```bash
chmod +x backend/scripts/setup.sh
docker-compose restart backend
docker-compose exec backend bash scripts/setup.sh
```

### Frontend ne se connecte pas au backend

Vérifier `.env` :
```bash
VITE_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:5173
```

---

## 📚 Prochaines étapes

- Lire le [README.md](README.md) complet
- Explorer le [guide RDF](docs/09-rdf-guide.md)
- Consulter la [documentation API](http://localhost:8000/docs)
- Personnaliser l'application pour votre cas d'usage
