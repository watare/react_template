# Setup Manuel (si auto-init échoue)

Si l'initialisation automatique ne fonctionne pas, suivez ces étapes :

## 1. Démarrer les services de base

```bash
cd template-webapp

# Démarrer PostgreSQL et Fuseki uniquement
docker-compose up -d postgres fuseki

# Attendre qu'ils soient prêts (30 secondes)
sleep 30
```

## 2. Vérifier que PostgreSQL et Fuseki sont prêts

```bash
# PostgreSQL
docker-compose exec postgres pg_isready -U postgres

# Fuseki
curl http://localhost:3030/$/ping
```

## 3. Initialiser la base de données manuellement

```bash
# Démarrer le backend temporairement
docker-compose run --rm backend bash

# Dans le container :
python scripts/init_db.py
python scripts/init_rdf.py
exit
```

## 4. Démarrer tous les services

```bash
# Maintenant démarrer backend et frontend
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

## 5. Tester

```bash
# Santé du backend
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

Si ça retourne un token, c'est bon ! ✅

Ouvrir http://localhost:5173 et se connecter avec `admin` / `admin`
