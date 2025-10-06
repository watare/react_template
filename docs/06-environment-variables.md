# Chapitre 6 : Variables d'Environnement

## Table des Matières
1. [Concept : Pourquoi des Variables d'Environnement ?](#concept--pourquoi-des-variables-denvironnement-)
2. [Frontend (Vite) : Variables VITE_](#frontend-vite--variables-vite_)
3. [Backend (FastAPI) : Variables Python](#backend-fastapi--variables-python)
4. [Fichiers .env : Organisation et Sécurité](#fichiers-env--organisation-et-sécurité)
5. [Docker & Docker Compose](#docker--docker-compose)
6. [Best Practices & Sécurité](#best-practices--sécurité)

---

## Concept : Pourquoi des Variables d'Environnement ?

### Le Problème

**Code en dur (MAUVAIS) :**
```typescript
// ❌ Ne jamais faire ça !
const API_URL = "http://localhost:8000"
const DB_PASSWORD = "secret123"
```

**Problèmes :**
- URL différente en dev/staging/production
- Passwords dans le code = faille de sécurité
- Impossible de changer sans recompiler
- Code versionné avec secrets

### La Solution : Variables d'Environnement

**Variables configurables en dehors du code :**
```typescript
// ✅ Bon
const API_URL = import.meta.env.VITE_API_URL
const DB_PASSWORD = process.env.DB_PASSWORD  // Backend seulement
```

**Avantages :**
- Configuration par environnement (dev/prod)
- Secrets hors du code
- Changement sans recompilation
- Sécurité renforcée

---

## Frontend (Vite) : Variables VITE_

### Règle Fondamentale

**Vite expose UNIQUEMENT les variables préfixées par `VITE_`**

```bash
# ✅ Accessible dans le frontend
VITE_API_URL=http://localhost:8000

# ❌ PAS accessible (pas de préfixe VITE_)
API_URL=http://localhost:8000
SECRET_KEY=abc123
```

**Pourquoi cette restriction ?**
- **Sécurité** : évite d'exposer des secrets dans le bundle JavaScript
- Le code frontend est visible par l'utilisateur (DevTools)
- Tout ce qui est dans le bundle peut être lu

### Créer des Variables Frontend

**Fichier `.env` (racine du projet frontend) :**
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=5000

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_MOCK_DATA=false

# App Info
VITE_APP_NAME=MyApp
VITE_APP_VERSION=1.0.0
```

### Utiliser les Variables dans le Code

**Syntaxe TypeScript/React :**
```typescript
// Accès direct
const apiUrl = import.meta.env.VITE_API_URL

// Avec valeur par défaut
const timeout = import.meta.env.VITE_API_TIMEOUT || 3000

// Type-safe avec validation
const isDebug = import.meta.env.VITE_ENABLE_DEBUG === 'true'
```

**Exemple concret :**
```typescript
// src/config/api.ts
export const API_CONFIG = {
  baseUrl: import.meta.env.VITE_API_URL,
  timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 5000,
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true'
}

// src/services/api.ts
import { API_CONFIG } from '../config/api'

async function fetchUsers() {
  const response = await fetch(`${API_CONFIG.baseUrl}/api/users`, {
    signal: AbortSignal.timeout(API_CONFIG.timeout)
  })
  return response.json()
}
```

### Types TypeScript pour les Variables

**Créer `src/vite-env.d.ts` :**
```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_ENABLE_DEBUG: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

**Avantage :** Autocomplétion et vérification de type

### Variables par Environnement

**Fichiers multiples :**
```
frontend/
├── .env                  # Variables par défaut
├── .env.development      # npm run dev
├── .env.production       # npm run build
└── .env.local            # Overrides locaux (non versionné)
```

**Exemple `.env.development` :**
```bash
VITE_API_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
```

**Exemple `.env.production` :**
```bash
VITE_API_URL=https://api.myapp.com
VITE_ENABLE_DEBUG=false
```

**Ordre de priorité (du plus fort au plus faible) :**
1. `.env.production.local` / `.env.development.local`
2. `.env.production` / `.env.development`
3. `.env.local`
4. `.env`

---

## Backend (FastAPI) : Variables Python

### Règle Fondamentale

**Le backend Python utilise TOUTES les variables (pas de préfixe obligatoire)**

**MAIS ATTENTION :**
- Ne JAMAIS exposer ces variables au frontend
- Garder les secrets côté serveur

### Méthode 1 : python-dotenv (Simple)

**Installation :**
```bash
pip install python-dotenv
```

**Fichier `backend/.env` :**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
FUSEKI_URL=http://localhost:3030
FUSEKI_DATASET=iec61850_project1

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Charger dans FastAPI (`backend/main.py`) :**
```python
from dotenv import load_dotenv
import os

# Charger le fichier .env
load_dotenv()

# Utiliser les variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set")

print(f"Connecting to database: {DATABASE_URL}")
```

### Méthode 2 : Pydantic Settings (Recommandé)

**Pourquoi Pydantic ?**
- Validation automatique des types
- Valeurs par défaut
- Documentation auto-générée
- Meilleure gestion d'erreurs

**Installation :**
```bash
pip install pydantic-settings
```

**Fichier `backend/config.py` :**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # RDF Store
    fuseki_url: str = "http://localhost:3030"
    fuseki_dataset: str = "iec61850_project1"

    # SMTP (optionnel)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # App
    debug: bool = False
    app_name: str = "MyApp"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False  # DATABASE_URL = database_url
    )

# Instance globale
settings = Settings()
```

**Utiliser dans FastAPI (`backend/main.py`) :**
```python
from fastapi import FastAPI
from config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

@app.on_event("startup")
async def startup():
    print(f"Connecting to DB: {settings.database_url}")
    print(f"Fuseki endpoint: {settings.fuseki_url}")

# Utiliser dans les routes
from sqlalchemy import create_engine
engine = create_engine(settings.database_url)
```

### Validation Avancée

**Avec validateurs Pydantic :**
```python
from pydantic import field_validator, AnyHttpUrl

class Settings(BaseSettings):
    database_url: str
    fuseki_url: AnyHttpUrl  # Valide que c'est une URL HTTP

    @field_validator('secret_key')
    def secret_key_min_length(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters')
        return v

    @field_validator('database_url')
    def validate_db_url(cls, v):
        if not v.startswith('postgresql://'):
            raise ValueError('DATABASE_URL must be PostgreSQL')
        return v
```

**Avantage :** Erreur claire au démarrage si config invalide

---

## Fichiers .env : Organisation et Sécurité

### Structure Recommandée

**Pour un projet fullstack :**
```
project/
├── frontend/
│   ├── .env                    # Variables frontend par défaut
│   ├── .env.development        # Dev frontend
│   ├── .env.production         # Prod frontend
│   └── .env.local              # Overrides locaux (NON VERSIONNÉ)
│
├── backend/
│   ├── .env                    # Variables backend (NON VERSIONNÉ)
│   ├── .env.example            # Template (versionné)
│   └── .env.test               # Variables pour tests
│
├── .env                        # Variables Docker Compose (NON VERSIONNÉ)
├── .env.example                # Template Docker (versionné)
└── docker-compose.yml
```

### Fichier .env.example (Template)

**Fichier `backend/.env.example` (À VERSIONNER) :**
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security (Generate with: openssl rand -hex 32)
SECRET_KEY=change-me-in-production

# RDF Store
FUSEKI_URL=http://localhost:3030
FUSEKI_DATASET=iec61850_project1

# SMTP (Optional)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
```

**Pourquoi .env.example ?**
- Documente les variables nécessaires
- Guide pour les nouveaux développeurs
- Template pour créer `.env`

**Setup pour nouveau dev :**
```bash
# Copier le template
cp backend/.env.example backend/.env

# Éditer avec les vraies valeurs
nano backend/.env
```

### Sécurité : .gitignore

**Fichier `.gitignore` :**
```bash
# Variables d'environnement (SECRETS)
.env
.env.local
.env.production.local
.env.development.local
backend/.env

# Templates à versionner
!.env.example
!backend/.env.example
```

**Règle d'or :**
- ❌ Ne JAMAIS committer `.env` avec secrets
- ✅ TOUJOURS committer `.env.example`

---

## Docker & Docker Compose

### Variables dans docker-compose.yml

**Méthode 1 : Fichier .env à la racine**

**Fichier `.env` (racine du projet) :**
```bash
# Database
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydb

# Backend
SECRET_KEY=supersecret
FUSEKI_URL=http://fuseki:3030

# Versions
POSTGRES_VERSION=16
PYTHON_VERSION=3.11
```

**Fichier `docker-compose.yml` :**
```yaml
version: '3.8'

services:
  db:
    image: postgres:${POSTGRES_VERSION}
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      SECRET_KEY: ${SECRET_KEY}
      FUSEKI_URL: ${FUSEKI_URL}
    depends_on:
      - db
      - fuseki
    ports:
      - "8000:8000"

  fuseki:
    image: stain/jena-fuseki
    environment:
      ADMIN_PASSWORD: ${FUSEKI_ADMIN_PASSWORD:-admin}  # Défaut: admin
    ports:
      - "3030:3030"

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
    ports:
      - "3000:80"
```

**Lancer avec les variables :**
```bash
docker-compose up
```

### Méthode 2 : Fichiers .env Séparés

**docker-compose.yml :**
```yaml
services:
  backend:
    build: ./backend
    env_file:
      - ./backend/.env        # Variables backend
      - ./.env.shared         # Variables partagées
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    env_file:
      - ./frontend/.env
    ports:
      - "3000:80"
```

### Build-time vs Runtime

**Variables au BUILD (Dockerfile) :**
```dockerfile
# frontend/Dockerfile
FROM node:18 AS build

WORKDIR /app

# Variables de build (fixées à la compilation)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

**Passer les args depuis docker-compose.yml :**
```yaml
services:
  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: ${VITE_API_URL}
```

**Variables au RUNTIME (backend Python) :**
```yaml
services:
  backend:
    image: mybackend:latest
    environment:
      DATABASE_URL: ${DATABASE_URL}  # Peut changer sans rebuild
```

---

## Best Practices & Sécurité

### 1. Ne Jamais Committer de Secrets

**❌ MAUVAIS :**
```bash
# .env (versionné avec git)
SECRET_KEY=abc123  # DANGEREUX !
DATABASE_PASSWORD=password123
```

**✅ BON :**
```bash
# .env.example (versionné)
SECRET_KEY=generate-with-openssl-rand-hex-32
DATABASE_PASSWORD=your-secure-password

# .gitignore
.env
```

### 2. Générer des Secrets Forts

**Générer une clé secrète :**
```bash
# Linux/macOS
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Utiliser dans `.env` :**
```bash
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### 3. Valeurs par Défaut Sécurisées

**❌ MAUVAIS :**
```python
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")  # Dangereux !
```

**✅ BON :**
```python
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")
```

### 4. Variables par Environnement

**Structure :**
```bash
# Dev
DATABASE_URL=postgresql://dev:dev@localhost:5432/dev_db
DEBUG=true

# Staging
DATABASE_URL=postgresql://staging:xxx@staging-db:5432/staging_db
DEBUG=false

# Production
DATABASE_URL=postgresql://prod:yyy@prod-db:5432/prod_db
DEBUG=false
```

**Charger selon l'environnement :**
```python
import os
from dotenv import load_dotenv

ENV = os.getenv("ENV", "development")
load_dotenv(f".env.{ENV}")
```

### 5. Documenter les Variables

**Fichier `ENVIRONMENT.md` :**
```markdown
# Variables d'Environnement

## Frontend (Vite)

| Variable | Description | Exemple | Requis |
|----------|-------------|---------|--------|
| VITE_API_URL | URL de l'API backend | http://localhost:8000 | Oui |
| VITE_ENABLE_DEBUG | Mode debug | true/false | Non (défaut: false) |

## Backend (FastAPI)

| Variable | Description | Exemple | Requis |
|----------|-------------|---------|--------|
| DATABASE_URL | PostgreSQL connection | postgresql://... | Oui |
| SECRET_KEY | JWT signing key | (généré) | Oui |
| FUSEKI_URL | RDF store endpoint | http://fuseki:3030 | Oui |
```

### 6. Rotation des Secrets

**Plan de rotation :**
```bash
# 1. Générer nouveau secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Mettre à jour .env
echo "SECRET_KEY=$NEW_SECRET" >> .env

# 3. Redémarrer le service
docker-compose restart backend

# 4. Révoquer l'ancien secret après période de grâce
```

---

## Résumé : Frontend vs Backend

| Aspect | Frontend (Vite) | Backend (FastAPI) |
|--------|----------------|-------------------|
| **Préfixe requis** | `VITE_` obligatoire | Aucun |
| **Syntaxe** | `import.meta.env.VITE_VAR` | `os.getenv("VAR")` |
| **Sécurité** | Exposé au client (public) | Privé (serveur) |
| **Secrets** | ❌ JAMAIS de secrets | ✅ Peut contenir secrets |
| **Fichier .env** | `frontend/.env` | `backend/.env` |
| **Build-time** | Fixé à la compilation | Runtime (modifiable) |
| **Validation** | TypeScript types | Pydantic Settings |

---

## Checklist : Setup Variables d'Environnement

### Frontend

- [ ] Créer `frontend/.env` avec variables `VITE_`
- [ ] Créer `frontend/.env.example` (template versionné)
- [ ] Ajouter types TypeScript (`vite-env.d.ts`)
- [ ] Vérifier `.gitignore` exclut `.env`
- [ ] Tester avec `import.meta.env.VITE_API_URL`

### Backend

- [ ] Créer `backend/.env` avec secrets
- [ ] Créer `backend/.env.example` (template)
- [ ] Installer `pydantic-settings`
- [ ] Créer `backend/config.py` avec classe Settings
- [ ] Valider au démarrage (erreur si vars manquantes)
- [ ] Vérifier `.gitignore` exclut `.env`

### Docker

- [ ] Créer `.env` à la racine (variables Docker)
- [ ] Créer `.env.example` (template)
- [ ] Configurer `docker-compose.yml` avec `${VAR}`
- [ ] Tester avec `docker-compose config` (affiche les valeurs)
- [ ] Documenter variables nécessaires

### Sécurité

- [ ] Générer `SECRET_KEY` avec `openssl rand -hex 32`
- [ ] Aucun secret dans le code ou git
- [ ] Fichiers `.env` dans `.gitignore`
- [ ] Documentation des variables requises
- [ ] Rotation régulière des secrets production

---

## Exemple Complet : Configuration Multi-Services

**Structure :**
```
project/
├── frontend/
│   ├── .env
│   └── .env.example
├── backend/
│   ├── .env
│   └── .env.example
├── .env                  # Docker Compose
├── .env.example
└── docker-compose.yml
```

**Fichier `.env` (racine - Docker Compose) :**
```bash
# Shared
POSTGRES_VERSION=16
PYTHON_VERSION=3.11

# Database
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydb

# RDF
FUSEKI_ADMIN_PASSWORD=adminpass

# URLs pour interconnexion
DATABASE_URL=postgresql://myuser:mypassword@db:5432/mydb
FUSEKI_URL=http://fuseki:3030
```

**Fichier `frontend/.env` :**
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=MyApp
```

**Fichier `backend/.env` :**
```bash
# Hérite de DATABASE_URL et FUSEKI_URL depuis docker-compose
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Fichier `docker-compose.yml` :**
```yaml
version: '3.8'

services:
  db:
    image: postgres:${POSTGRES_VERSION}
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}

  fuseki:
    image: stain/jena-fuseki
    environment:
      ADMIN_PASSWORD: ${FUSEKI_ADMIN_PASSWORD}

  backend:
    build: ./backend
    env_file:
      - ./backend/.env
    environment:
      DATABASE_URL: ${DATABASE_URL}
      FUSEKI_URL: ${FUSEKI_URL}
    depends_on:
      - db
      - fuseki

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
```

**Lancement :**
```bash
# Dev
docker-compose up

# Production (avec .env.production)
docker-compose --env-file .env.production up -d
```

---

Ce guide couvre tout ce qu'il faut savoir sur les variables d'environnement dans une architecture fullstack moderne !
