# Guide de Déploiement Complet : De Zéro à une Application Fonctionnelle

**Version 2025 - Projet d'Apprentissage Local**

---

## 🎯 Introduction : Ce que vous allez construire

Ce guide vous accompagne **étape par étape** pour déployer une application complète avec :
- **React + TypeScript** (Frontend)
- **FastAPI + Python** (Backend)
- **PostgreSQL** (Base de données relationnelle)
- **Apache Jena Fuseki** (Base RDF - optionnel)
- **JWT + RBAC** (Authentification et autorisations)

**Approche :** Chaque étape comprend :
- ✅ **Actions précises** à effectuer
- ⚠️ **Points d'attention critiques**
- 🧪 **Tests de validation** pour vérifier que tout fonctionne
- 🛑 **Points d'arrêt** si quelque chose ne fonctionne pas

**Important :** Ce guide est pour un **environnement local d'apprentissage** (localhost). Aucun déploiement sur serveur distant tant que vous ne le demandez pas explicitement.

---

## 📋 Phase 0 : Vérifications Préalables

### Étape 0.1 : Vérifier les Outils Installés

**Actions :**

```bash
# Vérifier Python (requis >= 3.11)
python3 --version

# Vérifier Node.js (requis >= 18)
node --version

# Vérifier Docker (requis >= 24.0)
docker --version

# Vérifier Docker Compose v2 (SANS tiret)
docker compose version

# Vérifier Git
git --version
```

**Points d'attention :**

- **Docker Compose v2** : La commande est `docker compose` (SANS tiret), pas `docker-compose`
- Si vous voyez `docker-compose version`, c'est la v1 (obsolète)
- Sur Windows WSL2, assurez-vous que Docker Desktop est démarré

**Tests de validation :**

```bash
# Toutes les commandes doivent retourner une version
# Exemple de sortie attendue :
# Python 3.11.x ou 3.12.x
# Node v18.x ou v20.x ou v22.x
# Docker version 24.x ou 25.x
# Docker Compose version v2.x.x
```

**Points d'arrêt critiques :**

Si Python < 3.11 :
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv

# macOS
brew install python@3.11

# Windows
# Télécharger depuis python.org
```

Si Node < 18 :
```bash
# Installer nvm (Node Version Manager) recommandé
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

**Checkpoint 0 :** ✅ Tous les outils sont installés avec les bonnes versions

---

### Étape 0.2 : Créer la Structure du Projet

**Actions :**

```bash
# Créer le dossier principal (si pas déjà fait)
mkdir -p ~/mooc-deployment
cd ~/mooc-deployment

# Créer la structure backend
mkdir -p backend/{db,auth,routes,schemas,scripts,rdf}
mkdir -p backend/alembic/versions

# Créer la structure frontend
mkdir -p frontend/src/{auth,components,features,api,store,app}

# Créer les fichiers de configuration
touch backend/{main.py,requirements.txt,.env}
touch frontend/{vite.config.ts,package.json,.env}
touch docker-compose.yml .gitignore README.md
```

**Créer `.gitignore` :**

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# Node
node_modules/
dist/
build/
.env.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
EOF
```

**Points d'attention :**

- **JAMAIS** commiter les fichiers `.env` (contiennent des secrets)
- Créer `.gitignore` **AVANT** le premier commit
- Respecter exactement cette structure pour la suite du guide

**Test de validation :**

```bash
# Vérifier la structure
tree -L 3 -a
# ou
find . -type f -o -type d | head -20
```

**Checkpoint 0.2 :** ✅ Structure de projet créée

---

## 🐘 Phase 1 : Démarrage des Bases de Données

### Étape 1.1 : Configuration Docker Compose

**Actions :**

Créer `docker-compose.yml` à la racine du projet :

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: mooc_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mooc_app
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  fuseki:
    image: stain/jena-fuseki:5.0.0
    container_name: mooc_fuseki
    ports:
      - "3030:3030"
    environment:
      ADMIN_PASSWORD: admin
      JVM_ARGS: "-Xmx2g"
    volumes:
      - fuseki_data:/fuseki
    restart: unless-stopped

volumes:
  postgres_data:
  fuseki_data:
```

**Points mis à jour 2025 :**

- ❌ **Pas de clé `version:`** (dépréciée depuis Compose v2)
- ✅ `postgres:16-alpine` (version stable actuelle, image légère)
- ✅ `jena-fuseki:5.0.0` (dernière version majeure)
- ✅ `restart: unless-stopped` pour redémarrage automatique
- ✅ `healthcheck` pour PostgreSQL (permet de vérifier qu'il est prêt)

**Test de validation :**

```bash
# Valider la syntaxe YAML
docker compose config

# Devrait afficher la config sans erreur
```

**Checkpoint 1.1 :** ✅ Docker Compose configuré

---

### Étape 1.2 : Démarrer les Conteneurs

**Actions :**

```bash
# Démarrer PostgreSQL et Fuseki
docker compose up -d

# Attendre que les conteneurs démarrent (10-20 secondes)
sleep 15

# Vérifier le statut
docker compose ps
```

**Points d'attention :**

- Les ports 5432 et 3030 doivent être **libres**
- Si erreur "port already in use", un service utilise déjà ce port

**Tests de validation :**

```bash
# Test 1 : PostgreSQL répond
docker compose exec postgres pg_isready -U postgres
# Attendu : "postgres:5432 - accepting connections"

# Test 2 : Connexion réelle PostgreSQL
docker compose exec postgres psql -U postgres -c "SELECT version();"
# Doit afficher : PostgreSQL 16.x

# Test 3 : Fuseki accessible
curl -s http://localhost:3030/$/ping
# Doit retourner : {"version": "5.0.0"}

# Test 4 : Statut des conteneurs
docker compose ps
# Les deux services doivent être "running" (postgres = healthy)

# Test 5 : Vérifier les logs (pas d'erreurs)
docker compose logs postgres --tail=20
docker compose logs fuseki --tail=20
```

**Points d'arrêt critiques :**

Si PostgreSQL ne démarre pas :
```bash
# Voir les logs complets
docker compose logs postgres

# Erreur courante : permission denied sur volume
# Solution : supprimer les volumes et recréer
docker compose down -v
docker compose up -d
```

Si port 5432 occupé :
```bash
# Linux/macOS : trouver le processus
sudo lsof -i :5432

# Windows : trouver le processus
netstat -ano | findstr :5432

# Arrêter le service conflictuel ou changer le port dans docker-compose.yml
```

Si Fuseki ne démarre pas :
```bash
# Vérifier les logs
docker compose logs fuseki

# Erreur courante : port 3030 occupé
# Solution : changer le port dans docker-compose.yml
# ports:
#   - "3031:3030"  # Utiliser 3031 localement
```

**Checkpoint 1.2 :** ✅ PostgreSQL et Fuseki démarrés et répondent

---

## 🐍 Phase 2 : Configuration Backend Python

### Étape 2.1 : Créer l'Environnement Virtuel

**Actions :**

```bash
cd backend

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement (choisir selon votre OS)

# Linux / macOS :
source venv/bin/activate

# Windows PowerShell :
.\venv\Scripts\Activate.ps1

# Windows CMD :
venv\Scripts\activate.bat
```

**Points d'attention :**

- Le prompt doit afficher `(venv)` après activation
- Toujours vérifier que le venv est actif avant d'installer des packages
- Sur Windows PowerShell, si erreur "scripts is disabled" :
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

**Test de validation :**

```bash
# Le prompt doit afficher (venv)
# Vérifier que python pointe vers le venv

# Linux/macOS
which python
# Doit afficher : /chemin/vers/backend/venv/bin/python

# Windows
where python
# Doit afficher : C:\chemin\vers\backend\venv\Scripts\python.exe
```

**Checkpoint 2.1 :** ✅ Environnement virtuel créé et activé

---

### Étape 2.2 : Installer les Dépendances Python

**Actions :**

Créer `backend/requirements.txt` :

```txt
# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.30.0

# Database
sqlalchemy==2.0.36
alembic==1.13.3
psycopg2-binary==2.9.10

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9

# Configuration & Validation
pydantic==2.9.0
pydantic-settings==2.5.0
python-dotenv==1.0.1

# HTTP Client
requests==2.32.0
httpx==0.27.0

# RDF (optionnel pour Phase 5)
rdflib==7.1.0
sparqlwrapper==2.0.0
```

Installer les dépendances :

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

**Points d'attention :**

- L'installation prend 2-3 minutes
- Vous verrez beaucoup de lignes défiler, c'est normal
- Sur Windows, `psycopg2-binary` peut nécessiter Visual C++ Build Tools

**Tests de validation :**

```bash
# Test 1 : Vérifier les packages installés
pip list | grep fastapi
pip list | grep sqlalchemy
pip list | grep alembic

# Test 2 : Versions spécifiques
pip show fastapi sqlalchemy alembic

# Test 3 : Import Python
python -c "import fastapi; import sqlalchemy; import alembic; print('✓ Imports OK')"

# Test 4 : Vérifier psycopg2
python -c "import psycopg2; print('✓ PostgreSQL driver OK')"
```

**Points d'arrêt critiques :**

Si erreur lors de l'installation de `psycopg2-binary` :

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libpq-dev

# macOS
brew install postgresql

# Windows
# Télécharger et installer Visual C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**Checkpoint 2.2 :** ✅ Dépendances Python installées

---

### Étape 2.3 : Configuration des Variables d'Environnement

**Actions :**

Créer `backend/.env` :

```bash
# Base de données PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mooc_app

# JWT - GÉNÉRER UN SECRET ALÉATOIRE EN PRODUCTION
JWT_SECRET=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# RDF
FUSEKI_URL=http://localhost:3030
FUSEKI_DATASET=mooc_project

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True
```

**Générer un JWT_SECRET sécurisé (optionnel en dev) :**

```bash
# Linux/macOS
openssl rand -hex 32

# Python (cross-platform)
python -c "import secrets; print(secrets.token_hex(32))"

# Copier le résultat dans JWT_SECRET
```

**Points d'attention CRITIQUES :**

- ⚠️ **JAMAIS** commiter le fichier `.env` dans Git
- ✅ Vérifier que `.env` est dans `.gitignore`
- ✅ En production, utiliser un vrai secret aléatoire (32+ caractères)
- ⚠️ Le mot de passe PostgreSQL ici (`postgres`) est OK pour le dev local, mais **jamais en production**

**Test de validation :**

```bash
# Vérifier que le fichier existe
cat .env | grep DATABASE_URL

# Vérifier que .env est ignoré par Git
git status
# .env ne doit PAS apparaître dans les fichiers à commiter

# Si .env apparaît dans git status, l'ajouter à .gitignore
echo ".env" >> ../.gitignore
```

**Checkpoint 2.3 :** ✅ Variables d'environnement configurées

---

## 🗄️ Phase 3 : Modèles de Données et Base

### Étape 3.1 : Créer les Modèles SQLAlchemy

**Actions :**

1. Créer `backend/db/__init__.py` (vide)

2. Créer `backend/db/models.py` :

```python
from sqlalchemy import Column, String, ForeignKey, Table, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional

class Base(DeclarativeBase):
    pass

# Tables de jonction (many-to-many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    roles: Mapped[list["Role"]] = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    users: Mapped[list["User"]] = relationship("User", secondary=user_roles, back_populates="roles")
    permissions: Mapped[list["Permission"]] = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    roles: Mapped[list["Role"]] = relationship("Role", secondary=role_permissions, back_populates="permissions")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payload_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
```

**Points mis à jour SQLAlchemy 2.0+ :**

- ✅ `Mapped[]` pour typage fort (PEP 484)
- ✅ `DeclarativeBase` au lieu de `declarative_base()`
- ✅ `mapped_column` au lieu de `Column` (syntaxe moderne)
- ✅ `datetime.now(timezone.utc)` au lieu de `datetime.utcnow()` (déprécié Python 3.12+)
- ✅ `ondelete="CASCADE"` sur les clés étrangères

**Points d'attention :**

- Respecter EXACTEMENT les noms de colonnes et tables
- Les relations `back_populates` doivent correspondre
- Ne pas oublier les index sur `email`, `code`, `name`

**Test de validation :**

```bash
cd backend
python -c "from db.models import User, Role, Permission, AuditLog, Base; print('✓ Modèles importés sans erreur')"
```

**Points d'arrêt critiques :**

- Si erreur d'import : vérifier que `__init__.py` existe dans `db/`
- Si erreur de syntaxe : comparer attentivement avec le code ci-dessus
- Si erreur `No module named 'db'` : vous n'êtes pas dans le bon dossier (`cd backend`)

**Checkpoint 3.1 :** ✅ Modèles SQLAlchemy créés et importables

---

### Étape 3.2 : Configuration Session et Settings

**Actions :**

Créer `backend/db/session.py` :

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Generator

class Settings(BaseSettings):
    """Configuration de l'application depuis .env"""

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    fuseki_url: str = "http://localhost:3030"
    fuseki_dataset: str = "mooc_project"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

# Instance globale des settings
settings = Settings()

# Engine SQLAlchemy avec pool de connexions
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,          # Vérifie que la connexion est vivante avant usage
    echo=settings.api_debug,     # Log SQL si debug=True
    pool_size=5,                 # 5 connexions permanentes
    max_overflow=10,             # +10 connexions en pic
    pool_recycle=3600            # Recycler les connexions après 1h
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator:
    """
    Dependency pour obtenir une session DB dans FastAPI

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Points mis à jour Pydantic 2.0+ :**

- ✅ `SettingsConfigDict` au lieu de `Config` inner class
- ✅ `model_config` au lieu de `class Config`
- ✅ `extra="ignore"` pour ignorer les variables d'env inconnues

**Test de validation :**

```bash
python -c "from db.session import settings, engine; print(f'✓ DB URL: {settings.database_url[:30]}...')"
```

**Checkpoint 3.2 :** ✅ Session SQLAlchemy configurée

---

### Étape 3.3 : Configuration Alembic pour les Migrations

**Actions :**

1. Initialiser Alembic :

```bash
cd backend
alembic init alembic
```

2. Modifier `alembic.ini` (ligne ~63) :

```ini
# Commenter ou supprimer cette ligne :
# sqlalchemy.url = driver://user:pass@localhost/dbname

# On utilisera l'URL depuis .env via env.py
```

3. **Remplacer TOUT LE CONTENU** de `alembic/env.py` :

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Importer les modèles et settings
from db.models import Base
from db.session import settings

# Configuration Alembic
config = context.config

# Définir l'URL de connexion depuis les settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configuration logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées pour autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Points d'attention :**

- Bien importer `Base` depuis `db.models`
- Bien importer `settings` depuis `db.session`
- Le `sys.path` permet d'importer les modules locaux

**Test de validation :**

```bash
# Vérifier qu'Alembic peut se connecter
alembic current

# Doit afficher : (rien ou "no current revision")
# PAS d'erreur de connexion
```

**Points d'arrêt critiques :**

- Erreur "No module named 'db'" : problème de `sys.path` dans env.py
- Erreur de connexion DB : vérifier que PostgreSQL est démarré (`docker compose ps`)
- Erreur "target_metadata is None" : vérifier l'import de Base

**Checkpoint 3.3 :** ✅ Alembic configuré et connecté à PostgreSQL

---

### Étape 3.4 : Créer et Appliquer la Migration Initiale

**Actions :**

1. Activer l'extension UUID dans PostgreSQL :

```bash
docker compose exec postgres psql -U postgres -d mooc_app -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

2. Générer la migration automatiquement :

```bash
cd backend
alembic revision --autogenerate -m "Create RBAC tables"
```

3. **CRITIQUE** : Ouvrir le fichier généré dans `alembic/versions/XXXXX_create_rbac_tables.py`

**Vérifier que la migration contient :**

```python
def upgrade() -> None:
    # Tables
    op.create_table('permissions', ...)
    op.create_table('roles', ...)
    op.create_table('users', ...)
    op.create_table('audit_logs', ...)
    op.create_table('user_roles', ...)
    op.create_table('role_permissions', ...)

    # Index UNIQUE
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_roles_name', 'roles', ['name'], unique=True)
    op.create_index('ix_permissions_code', 'permissions', ['code'], unique=True)
```

4. Appliquer la migration :

```bash
alembic upgrade head
```

**Tests de validation :**

```bash
# Test 1 : Migration appliquée
alembic current
# Doit afficher le hash de la migration (ex: "abc123def456 (head)")

# Test 2 : Tables créées
docker compose exec postgres psql -U postgres -d mooc_app -c "\dt"
# Doit lister : alembic_version, audit_logs, permissions, role_permissions, roles, user_roles, users

# Test 3 : Structure de la table users
docker compose exec postgres psql -U postgres -d mooc_app -c "\d users"

# Test 4 : Index créés
docker compose exec postgres psql -U postgres -d mooc_app -c "\di"

# Test 5 : Contraintes (clés étrangères avec CASCADE)
docker compose exec postgres psql -U postgres -d mooc_app -c "
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
"
```

**Points d'arrêt critiques :**

Si `alembic upgrade head` échoue avec erreur UUID :
```bash
# Activer l'extension UUID
docker compose exec postgres psql -U postgres -d mooc_app -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
# Puis refaire
alembic upgrade head
```

Si tables manquantes :
```bash
# Vérifier que tous les modèles sont importés dans db/models.py
# Supprimer la migration et la recréer
alembic downgrade base
rm alembic/versions/*.py
alembic revision --autogenerate -m "Create RBAC tables"
alembic upgrade head
```

**Checkpoint 3.4 :** ✅ Migration appliquée, tables créées dans PostgreSQL

---

### Étape 3.5 : Créer les Scripts d'Authentification

**Actions :**

1. Créer `backend/auth/__init__.py` (vide)

2. Créer `backend/auth/password.py` :

```python
from passlib.context import CryptContext

# Configuration bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt

    Args:
        password: Mot de passe en clair

    Returns:
        Hash bcrypt du mot de passe
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe contre son hash

    Args:
        plain_password: Mot de passe en clair à vérifier
        hashed_password: Hash bcrypt stocké

    Returns:
        True si le mot de passe correspond, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)
```

3. Créer `backend/auth/jwt.py` :

```python
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from db.session import settings
from typing import Dict, Any, Optional

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un JWT token

    Args:
        data: Données à encoder dans le token (sub, email, perms, etc.)
        expires_delta: Durée de validité personnalisée (optionnel)

    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Décode et valide un JWT token

    Args:
        token: Token JWT à décoder

    Returns:
        Payload du token décodé

    Raises:
        JWTError: Si le token est invalide ou expiré
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm]
    )
    return payload
```

**Points mis à jour 2025 :**

- ✅ `datetime.now(timezone.utc)` au lieu de `datetime.utcnow()` (déprécié Python 3.12+)
- ✅ Ajout de `iat` (issued at) dans le token

**Tests de validation :**

```bash
# Test 1 : Hash password
python -c "
from auth.password import hash_password, verify_password
h = hash_password('test123')
print('✓ Hash:', h[:20] + '...')
print('✓ Verify correct:', verify_password('test123', h))
print('✓ Verify wrong:', not verify_password('wrong', h))
"

# Test 2 : JWT
python -c "
from auth.jwt import create_access_token, decode_access_token
token = create_access_token({'sub': 'test-user-id', 'email': 'test@example.com'})
print('✓ Token créé:', token[:30] + '...')
payload = decode_access_token(token)
print('✓ Token décodé:', payload)
"
```

**Checkpoint 3.5 :** ✅ Système d'authentification fonctionnel

---

### Étape 3.6 : Script de Seed (Données Initiales)

**Actions :**

1. Créer `backend/scripts/__init__.py` (vide)

2. Créer `backend/scripts/seed.py` :

```python
"""
Script d'initialisation de la base de données
Crée les rôles, permissions et utilisateurs de démonstration
"""
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.models import User, Role, Permission
from auth.password import hash_password
from uuid import uuid4

def seed_database():
    """Initialise la base avec données de démo"""
    print("🌱 Initialisation de la base de données...")

    with SessionLocal() as db:
        # Vérifier si déjà seedé
        if db.query(Role).count() > 0:
            print("✓ Base déjà initialisée")
            return

        print("📝 Création des permissions...")
        # Créer permissions
        perms = {
            'dashboard:view': Permission(
                id=uuid4(),
                code='dashboard:view',
                description='Accéder au tableau de bord'
            ),
            'nodes:view': Permission(
                id=uuid4(),
                code='nodes:view',
                description='Voir les nœuds'
            ),
            'nodes:edit': Permission(
                id=uuid4(),
                code='nodes:edit',
                description='Modifier les nœuds'
            ),
            'nodes:delete': Permission(
                id=uuid4(),
                code='nodes:delete',
                description='Supprimer les nœuds'
            ),
            'admin:access': Permission(
                id=uuid4(),
                code='admin:access',
                description="Accéder à l'interface d'administration"
            ),
            'users:manage': Permission(
                id=uuid4(),
                code='users:manage',
                description='Gérer les utilisateurs et les rôles'
            ),
        }
        db.add_all(perms.values())
        db.flush()
        print(f"  ✓ {len(perms)} permissions créées")

        print("👥 Création des rôles...")
        # Créer rôles
        admin_role = Role(
            id=uuid4(),
            name='ADMIN',
            description='Administrateur système - Accès complet'
        )
        admin_role.permissions = list(perms.values())

        engineer_role = Role(
            id=uuid4(),
            name='ENGINEER',
            description='Ingénieur - Peut consulter et modifier'
        )
        engineer_role.permissions = [
            perms['dashboard:view'],
            perms['nodes:view'],
            perms['nodes:edit']
        ]

        viewer_role = Role(
            id=uuid4(),
            name='VIEWER',
            description='Lecteur - Consultation uniquement'
        )
        viewer_role.permissions = [
            perms['dashboard:view'],
            perms['nodes:view']
        ]

        db.add_all([admin_role, engineer_role, viewer_role])
        db.flush()
        print("  ✓ 3 rôles créés (ADMIN, ENGINEER, VIEWER)")

        print("🔐 Création des utilisateurs...")
        # Créer utilisateurs
        admin_user = User(
            id=uuid4(),
            email='admin@localhost',
            password_hash=hash_password('admin123'),
            full_name='Administrateur',
            is_active=True
        )
        admin_user.roles.append(admin_role)

        engineer_user = User(
            id=uuid4(),
            email='engineer@localhost',
            password_hash=hash_password('engineer123'),
            full_name='Ingénieur',
            is_active=True
        )
        engineer_user.roles.append(engineer_role)

        viewer_user = User(
            id=uuid4(),
            email='viewer@localhost',
            password_hash=hash_password('viewer123'),
            full_name='Visiteur',
            is_active=True
        )
        viewer_user.roles.append(viewer_role)

        db.add_all([admin_user, engineer_user, viewer_user])

        # Commit final
        db.commit()

        print("\n✅ Base initialisée avec succès!")
        print("\n" + "="*60)
        print("👤 Comptes de test créés:")
        print("="*60)
        print("📧 admin@localhost       🔑 admin123       👑 ADMIN")
        print("📧 engineer@localhost    🔑 engineer123    🔧 ENGINEER")
        print("📧 viewer@localhost      🔑 viewer123      👀 VIEWER")
        print("="*60)
        print("\n⚠️  IMPORTANT: Ceci est pour l'apprentissage uniquement!\n")

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"\n❌ Erreur lors du seed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
```

3. Exécuter le seed :

```bash
cd backend
python scripts/seed.py
```

**Tests de validation :**

```bash
# Test 1 : Compter les rôles
docker compose exec postgres psql -U postgres -d mooc_app -c "SELECT name, description FROM roles ORDER BY name;"

# Test 2 : Compter les permissions
docker compose exec postgres psql -U postgres -d mooc_app -c "SELECT COUNT(*) FROM permissions;"
# Doit retourner : 6

# Test 3 : Vérifier les utilisateurs
docker compose exec postgres psql -U postgres -d mooc_app -c "SELECT email, full_name, is_active FROM users ORDER BY email;"

# Test 4 : Vérifier les permissions de l'ADMIN
docker compose exec postgres psql -U postgres -d mooc_app -c "
SELECT r.name, COUNT(p.id) as nb_permissions, string_agg(p.code, ', ' ORDER BY p.code) as permissions
FROM roles r
LEFT JOIN role_permissions rp ON r.id = rp.role_id
LEFT JOIN permissions p ON rp.permission_id = p.id
GROUP BY r.name
ORDER BY r.name;
"

# Test 5 : Hash du mot de passe
docker compose exec postgres psql -U postgres -d mooc_app -c "SELECT email, LEFT(password_hash, 10) as hash_prefix FROM users WHERE email='admin@localhost';"
# Le hash doit commencer par "$2b$"
```

**Checkpoint 3.6 :** ✅ Données initiales chargées (3 rôles, 3 users, 6 permissions)

---

## 🚀 Phase 4 : API Backend FastAPI

### Étape 4.1 : Créer les Dependencies d'Authentification

**Actions :**

Créer `backend/auth/dependencies.py` :

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from db.session import get_db
from db.models import User
from auth.jwt import decode_access_token
from typing import Callable

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Récupère l'utilisateur courant depuis le JWT
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide: identifiant utilisateur manquant",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide ou expiré: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte utilisateur désactivé"
        )

    return user

def require_permission(permission_code: str) -> Callable:
    """
    Crée une dépendance qui vérifie qu'un utilisateur a une permission

    Usage:
        @router.get("/admin", dependencies=[Depends(require_permission("admin:access"))])
        def admin_page():
            return {"message": "Admin area"}
    """
    def permission_checker(user: User = Depends(get_current_user)) -> User:
        # Collecter toutes les permissions de l'utilisateur
        user_perms = set()
        for role in user.roles:
            for perm in role.permissions:
                user_perms.add(perm.code)

        if permission_code not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission requise: {permission_code}"
            )

        return user

    return permission_checker
```

**Checkpoint 4.1 :** ✅ Dependencies d'authentification créées

---

### Étape 4.2 : Créer les Schemas Pydantic

**Actions :**

1. Créer `backend/schemas/__init__.py` (vide)

2. Créer `backend/schemas/auth.py` :

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class LoginRequest(BaseModel):
    """Requête de connexion"""
    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., min_length=6, description="Mot de passe")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "admin@localhost",
                    "password": "admin123"
                }
            ]
        }
    )

class LoginResponse(BaseModel):
    """Réponse de connexion"""
    access_token: str = Field(..., description="Token JWT")
    token_type: str = Field(default="bearer", description="Type de token")

class UserResponse(BaseModel):
    """Informations utilisateur"""
    sub: str = Field(..., description="ID utilisateur")
    email: str = Field(..., description="Email")
    full_name: Optional[str] = Field(None, description="Nom complet")
    roles: list[str] = Field(default_factory=list, description="Liste des rôles")
    perms: list[str] = Field(default_factory=list, description="Liste des permissions")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "sub": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "admin@localhost",
                    "full_name": "Administrateur",
                    "roles": ["ADMIN"],
                    "perms": ["dashboard:view", "admin:access"]
                }
            ]
        }
    )
```

**Checkpoint 4.2 :** ✅ Schemas Pydantic créés

---

### Étape 4.3 : Créer les Routes d'Authentification

**Actions :**

1. Créer `backend/routes/__init__.py` (vide)

2. Créer `backend/routes/auth.py` :

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User
from auth.password import verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user
from schemas.auth import LoginRequest, LoginResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentification"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Connexion utilisateur

    Vérifie les identifiants et retourne un JWT si valides
    """
    # Chercher l'utilisateur par email
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Vérifier le mot de passe
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Vérifier que le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )

    # Collecter les permissions
    perms = set()
    for role in user.roles:
        for perm in role.permissions:
            perms.add(perm.code)

    # Créer le token JWT
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "perms": list(perms)
    })

    return LoginResponse(access_token=token)

@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur connecté
    """
    # Collecter permissions et rôles
    perms = set()
    roles = []

    for role in user.roles:
        roles.append(role.name)
        for perm in role.permissions:
            perms.add(perm.code)

    return UserResponse(
        sub=str(user.id),
        email=user.email,
        full_name=user.full_name,
        roles=roles,
        perms=list(perms)
    )

@router.post("/logout")
def logout():
    """
    Déconnexion

    Avec JWT, la déconnexion se fait côté client (suppression du token)
    """
    return {"message": "Déconnexion réussie"}
```

**Checkpoint 4.3 :** ✅ Routes d'authentification créées

---

### Étape 4.4 : Créer l'Application FastAPI Principale

**Actions :**

Créer `backend/main.py` :

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.session import settings
from routes import auth
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage
    logger.info("🚀 Démarrage de l'application")
    logger.info(f"📊 Base de données configurée")
    logger.info(f"🔐 JWT expire après: {settings.jwt_expire_minutes} minutes")

    yield

    # Arrêt
    logger.info("🛑 Arrêt de l'application")

# Création de l'application FastAPI
app = FastAPI(
    title="MOOC Learning App",
    description="""
    API complète avec authentification JWT et RBAC.

    ## Comptes de test

    * `admin@localhost` / `admin123` - Administrateur
    * `engineer@localhost` / `engineer123` - Ingénieur
    * `viewer@localhost` / `viewer123` - Lecteur
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev
        "http://localhost:3000",  # Alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(auth.router)

# Routes de base
@app.get("/", tags=["Système"])
def root():
    """Page d'accueil de l'API"""
    return {
        "message": "MOOC Learning API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Système"])
def health():
    """Health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
```

**Checkpoint 4.4 :** ✅ Application FastAPI créée

---

### Étape 4.5 : Démarrer l'API Backend

**Actions :**

```bash
cd backend

# S'assurer que venv est activé (prompt doit afficher (venv))

# Démarrer l'API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Tests de validation :**

```bash
# Test 1 : API répond
curl http://localhost:8000/
# Doit retourner : {"message": "MOOC Learning API", ...}

# Test 2 : Health check
curl http://localhost:8000/health
# Doit retourner : {"status": "healthy"}

# Test 3 : Documentation auto-générée
curl -I http://localhost:8000/docs
# Doit retourner : HTTP/1.1 200 OK

# Test 4 : Login ADMIN
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@localhost","password":"admin123"}' | jq

# Test 5 : /me avec token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@localhost","password":"admin123"}' \
  | jq -r '.access_token')

curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Checkpoint 4.5 :** ✅ API Backend fonctionnelle

---

## 📝 Résumé : Ce que vous avez construit

### ✅ Infrastructure

- PostgreSQL pour les données relationnelles
- Fuseki pour les données RDF (préparé)
- Docker Compose pour orchestrer les services

### ✅ Backend

- FastAPI avec routes d'authentification
- SQLAlchemy avec modèles User, Role, Permission
- Alembic pour les migrations
- JWT pour l'authentification
- RBAC avec permissions granulaires
- 3 utilisateurs de test

### ✅ Prochaines Étapes

Maintenant que le backend est fonctionnel, vous pouvez :

1. **Tester l'API avec Postman ou curl**
2. **Créer le frontend React** (voir docs/frontend-setup.md)
3. **Ajouter des routes protégées**
4. **Intégrer RDF avec Fuseki** (Phase 5)

---

## 🐛 Troubleshooting

### Problème : PostgreSQL ne démarre pas

```bash
# Voir les logs
docker compose logs postgres

# Solution : Supprimer les volumes et recréer
docker compose down -v
docker compose up -d
```

### Problème : Alembic ne trouve pas les modèles

```bash
# Vérifier les imports dans alembic/env.py
python -c "from db.models import Base; print(Base.metadata.tables.keys())"
```

### Problème : JWT invalide

```bash
# Vérifier que JWT_SECRET est défini dans .env
cat backend/.env | grep JWT_SECRET
```

---

**Guide créé le 2025-10-06 pour le projet d'apprentissage MOOC**
