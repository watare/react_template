# Clarifications Essentielles : Migrations, FastAPI et Architecture

*Cette section répond aux questions fondamentales sur l'architecture moderne du web : pourquoi FastAPI ? Comment React communique avec la base ? Pourquoi des migrations ? Approche pédagogique : du débutant à l'avancé.*

---

## 1. Migrations : Pourquoi et Quand ?

**Question clé :** Pourquoi utiliser une migration Alembic pour insérer des données initiales (seed) ?

### Les Deux Usages des Migrations

**Usage Principal : Gestion du Schéma**

Les migrations sont conçues pour versioner la **structure** de la base de données :

```python
# Migration : Créer une table
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False)
    )

# Migration : Ajouter une colonne
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20)))

# Migration : Modifier un type
def upgrade():
    op.alter_column('users', 'phone', type_=sa.String(30))
```

**Usage Secondaire : Données Initiales Critiques**

Les migrations peuvent aussi insérer des **données de base** nécessaires au fonctionnement :

```python
# Migration : Insérer les rôles système
def upgrade():
    op.execute("""
        INSERT INTO roles (id, name, description) VALUES
        ('uuid-admin', 'ADMIN', 'Super administrateur'),
        ('uuid-user', 'USER', 'Utilisateur standard')
    """)
```

### Quand Utiliser Quelle Approche ?

**Tableau décisionnel :**

| Type de données | Approche | Raison | Exemple |
|-----------------|----------|--------|---------|
| **Structure** (tables, colonnes, index) | Migration Alembic ✅ | Doit évoluer avec le code | `CREATE TABLE users` |
| **Rôles/permissions système** | Migration Alembic ✅ | Critiques pour le fonctionnement | `ADMIN`, `USER` |
| **Premier admin** | Script seed séparé ⚙️ | Varie selon l'environnement | `admin@dev.local` vs `admin@prod.com` |
| **Données de test** | Script seed séparé ⚙️ | Uniquement en dev | 100 utilisateurs fictifs |
| **Données métier** | Interface utilisateur 🖥️ | Créées par les utilisateurs | Articles, commandes |

### Approche 1 : Seed dans la Migration (Recommandé pour les Rôles)

**Avantages :**
- **Reproductibilité** : chaque environnement (dev, staging, prod) a les mêmes rôles
- **Versioning** : les rôles sont dans Git avec le code
- **Automatisation** : `alembic upgrade head` crée tables ET données
- **Ordre garanti** : les rôles sont créés après les tables, automatiquement

**Inconvénients :**
- Mélange structure et contenu (moins "propre" conceptuellement)
- Difficile à maintenir si les données changent souvent

**Exemple complet :**

```python
# migrations/versions/002_seed_roles.py
from alembic import op
import sqlalchemy as sa
from uuid import uuid4

def upgrade():
    # Créer les rôles de base
    roles_table = sa.table(
        'roles',
        sa.column('id', sa.UUID()),
        sa.column('name', sa.String()),
        sa.column('description', sa.String())
    )

    op.bulk_insert(roles_table, [
        {
            'id': uuid4(),
            'name': 'ADMIN',
            'description': 'Super administrateur'
        },
        {
            'id': uuid4(),
            'name': 'USER',
            'description': 'Utilisateur standard'
        }
    ])

def downgrade():
    # Supprimer les rôles
    op.execute("DELETE FROM roles WHERE name IN ('ADMIN', 'USER')")
```

**Utilisation :**
```bash
# Une seule commande crée tout
alembic upgrade head
```

### Approche 2 : Script Seed Séparé (Recommandé pour les Tests)

**Plus propre conceptuellement**, mais nécessite deux étapes.

**Exemple :**

```python
# scripts/seed.py
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.models import User, Role
import bcrypt

def seed_database():
    db = SessionLocal()

    try:
        # 1. Créer les rôles (si pas dans migration)
        admin_role = Role(name='ADMIN', description='Super admin')
        user_role = Role(name='USER', description='Utilisateur')
        db.add_all([admin_role, user_role])
        db.commit()

        # 2. Créer le premier admin
        admin_user = User(
            email='admin@localhost',
            password_hash=bcrypt.hashpw(b'admin123', bcrypt.gensalt())
        )
        admin_user.roles.append(admin_role)
        db.add(admin_user)

        # 3. Créer des utilisateurs de test
        for i in range(10):
            test_user = User(
                email=f'user{i}@localhost',
                password_hash=bcrypt.hashpw(b'test123', bcrypt.gensalt())
            )
            test_user.roles.append(user_role)
            db.add(test_user)

        db.commit()
        print("✅ Base de données seedée avec succès")

    finally:
        db.close()

if __name__ == '__main__':
    seed_database()
```

**Utilisation :**
```bash
# 1. Structure
alembic upgrade head

# 2. Données
python scripts/seed.py
```

### Notre Choix pour ce Projet

**Stratégie hybride :**
- **Rôles système** → Migration Alembic (critiques, stables)
- **Premier admin** → Script seed (varie dev/prod)
- **Données de test** → Script seed (uniquement dev)

```bash
# Setup complet en développement
alembic upgrade head      # Tables + rôles système
python scripts/seed.py    # Admin + données de test

# Setup en production
alembic upgrade head      # Tables + rôles système
# Puis créer l'admin manuellement via interface sécurisée
```

---

## 2. Pourquoi FastAPI ? PostgreSQL ne Suffit-il Pas ?

**Question clé :** Si PostgreSQL stocke les données, pourquoi ne pas s'y connecter directement depuis React ?

### Le Mythe de la Connexion Directe

**Ce qu'on pourrait imaginer (mais qui est IMPOSSIBLE) :**

```tsx
// ❌ IMPOSSIBLE depuis le navigateur
import postgres from 'postgres'  // N'existe pas côté navigateur !

const db = postgres('postgresql://user:password@localhost:5432/mydb')
const users = await db`SELECT * FROM users`

return <ul>{users.map(u => <li>{u.email}</li>)}</ul>
```

### Pourquoi C'est Techniquement Impossible ?

**Trois raisons fondamentales :**

**1. Sécurité du Navigateur (Sandbox)**

Les navigateurs modernes isolent JavaScript pour la sécurité :

```
✅ Autorisé :
- fetch() vers HTTP/HTTPS
- WebSocket vers ws://wss://
- Accès au localStorage, cookies

❌ Bloqué :
- Connexions TCP/IP directes
- Accès au système de fichiers
- Connexions à des ports arbitraires (comme 5432)
```

**Pourquoi ?** Si JavaScript pouvait ouvrir des connexions TCP, un site malveillant pourrait scanner votre réseau local, attaquer votre routeur, etc.

**2. Protocole PostgreSQL**

PostgreSQL utilise un protocole binaire propriétaire :

```
┌──────────────────────────────────────┐
│ Application Python                   │
│ psycopg2.connect() ──> TCP:5432     │  ✅ Fonctionne
│ Parle le protocole PostgreSQL        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Navigateur Web                       │
│ fetch() ──> HTTP:80 / HTTPS:443     │  ✅ Fonctionne
│ Parle uniquement HTTP(S)             │
│                                      │
│ ??? ──> TCP:5432                    │  ❌ Impossible
│ Ne sait pas parler PostgreSQL        │
└──────────────────────────────────────┘
```

**3. Sécurité des Credentials**

```javascript
// Si on pouvait faire ça dans React...
const db = postgres('postgresql://admin:SuperSecret123@localhost:5432/mydb')

// Problème: Ce code est téléchargé chez l'utilisateur !
// N'importe qui peut ouvrir DevTools et voir:
// - Le mot de passe PostgreSQL
// - L'IP du serveur
// - Le nom de la base
```

**Conséquence :** Exposer les credentials PostgreSQL dans le frontend = catastrophe de sécurité

### Ce que FastAPI Fait Réellement

FastAPI est une **couche intermédiaire obligatoire** entre le frontend et la base de données.

**Architecture complète :**

```
┌─────────────────────────────────────────────────────────────┐
│ NAVIGATEUR (Localhost:5173)                                 │
│                                                             │
│  React Component                                            │
│  ↓                                                          │
│  fetch('/api/users')  ──────────────────┐                  │
│  (HTTP GET)                              │                  │
└──────────────────────────────────────────┼──────────────────┘
                                           │
                                           │ HTTP (Port 80/443)
                                           │
┌──────────────────────────────────────────┼──────────────────┐
│ SERVEUR FASTAPI (Localhost:8000)         ↓                  │
│                                                             │
│  @app.get('/api/users')                                     │
│  ↓                                                          │
│  db.query(User).all()  ──────────────────┐                 │
│  (SQLAlchemy)                             │                 │
└───────────────────────────────────────────┼─────────────────┘
                                            │
                                            │ PostgreSQL Protocol
                                            │ (Port 5432)
                                            │
┌───────────────────────────────────────────┼─────────────────┐
│ POSTGRESQL (Localhost:5432)               ↓                 │
│                                                             │
│  SELECT * FROM users;                                       │
│  ↓                                                          │
│  [rows] ──> SQLAlchemy ──> FastAPI ──> React               │
└─────────────────────────────────────────────────────────────┘
```

### Les 3 Rôles de FastAPI

**Rôle 1 : Traduction de Protocole**

FastAPI traduit HTTP (compris par le navigateur) en SQL (compris par PostgreSQL) :

```python
# Le navigateur envoie:
GET /api/users HTTP/1.1
Host: localhost:8000

# FastAPI traduit en:
SELECT id, email, created_at FROM users;

# PostgreSQL retourne:
[
  (uuid('123...'), 'marie@example.com', datetime(...)),
  (uuid('456...'), 'paul@example.com', datetime(...))
]

# FastAPI retransforme en JSON:
HTTP/1.1 200 OK
Content-Type: application/json

[
  {"id": "123...", "email": "marie@example.com"},
  {"id": "456...", "email": "paul@example.com"}
]

# React reçoit du JSON utilisable !
```

**Rôle 2 : Sécurité**

FastAPI centralise toutes les vérifications de sécurité :

```python
from fastapi import Depends, HTTPException
from jose import jwt

@app.get('/api/users')
async def get_users(
    current_user: User = Depends(get_current_user)  # Vérif JWT
):
    # 1. JWT décodé et validé
    # 2. User récupéré depuis la DB
    # 3. Permissions vérifiées

    if not current_user.has_permission('users:read'):
        raise HTTPException(403, "Permission refusée")

    # Seulement maintenant on query
    users = db.query(User).all()
    return users
```

**Vérifications impossibles côté frontend :**
- Valider un JWT (secret stocké côté serveur)
- Hasher un mot de passe avec bcrypt
- Vérifier les permissions réelles (frontend = pas fiable)

**Rôle 3 : Logique Métier**

FastAPI ne fait pas que relayer les requêtes, il exécute de la **logique métier complexe** :

```python
@app.post('/api/users')
async def create_user(email: str, password: str, db: Session = Depends(get_db)):
    # 1. Validation métier
    if not is_valid_email(email):
        raise HTTPException(400, "Email invalide")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email déjà utilisé")

    # 2. Transformation sécurisée
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # 3. Transaction multi-tables
    user = User(email=email, password_hash=password_hash)
    db.add(user)

    default_role = db.query(Role).filter(Role.name == 'USER').first()
    user.roles.append(default_role)

    db.commit()

    # 4. Effets de bord
    send_welcome_email(user.email)
    log_audit('user_created', user.id)

    # 5. Retour formaté
    return {"id": str(user.id), "email": user.email}
```

**Cette logique ne peut PAS être dans React car :**
- Validation côté frontend = contournable (DevTools)
- Hashing côté frontend = inutile (intercepté avant hashage)
- Emails envoyés côté frontend = impossible (pas de serveur SMTP)

---

## 3. Vite Proxy : Pourquoi Pas Directement PostgreSQL ?

**Question :** `vite.config.ts` peut configurer un proxy, pourquoi pas vers PostgreSQL ?

### Ce que Vite PEUT Faire

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Redirige vers FastAPI
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

**Ce qui se passe :**

```
React fait:
fetch('/api/users')
        ↓
Vite intercepte et transforme en:
http://localhost:8000/users
        ↓
FastAPI reçoit la requête
```

**Utilité :** Éviter les problèmes CORS en développement.

### Ce que Vite NE PEUT PAS Faire

```typescript
// ❌ IMPOSSIBLE - Cette config n'existe pas
export default defineConfig({
  server: {
    database: {
      host: 'localhost',
      port: 5432,
      user: 'postgres',
      password: 'secret'
    }
  }
})
```

**Pourquoi ?** Vite est un **outil de build frontend**, pas un serveur applicatif :

```
┌──────────────────────────────────────┐
│ Vite                                 │
│ - Compile TypeScript → JavaScript   │
│ - Bundle les modules                 │
│ - Hot Module Replacement (HMR)       │
│ - Dev server HTTP pour fichiers      │
│ - Proxy HTTP vers autres serveurs    │
└──────────────────────────────────────┘
        ↑
        └─ Compétences limitées à HTTP

┌──────────────────────────────────────┐
│ FastAPI                              │
│ - Serveur applicatif complet         │
│ - Connexion PostgreSQL               │
│ - Logique métier                     │
│ - Authentification JWT               │
│ - ORM (SQLAlchemy)                   │
└──────────────────────────────────────┘
        ↑
        └─ Serveur applicatif complet
```

**Vite ne peut proxyer QUE du HTTP**, pas du PostgreSQL.

---

## 4. React Query : Comment Consulter la Base depuis React ?

**Architecture complète avec React Query :**

```
┌─────────────────────────────────────────────────────┐
│ NAVIGATEUR                                          │
│                                                     │
│  ┌──────────────┐                                  │
│  │ Component    │                                  │
│  │ UsersList    │                                  │
│  └──────┬───────┘                                  │
│         │                                           │
│         ↓ useQuery()                                │
│  ┌──────────────┐                                  │
│  │ React Query  │                                  │
│  │ - Cache      │                                  │
│  │ - Retry      │                                  │
│  │ - Loading    │                                  │
│  └──────┬───────┘                                  │
│         │                                           │
│         ↓ fetch()                                   │
│  ┌──────────────┐                                  │
│  │ /api/users   │                                  │
│  └──────┬───────┘                                  │
└─────────┼───────────────────────────────────────────┘
          │ HTTP (Vite proxy: 5173 → 8000)
          ↓
┌─────────┼───────────────────────────────────────────┐
│ SERVEUR │                                           │
│         ↓                                           │
│  ┌──────────────┐                                  │
│  │ @router.get  │                                  │
│  │ /api/users   │                                  │
│  └──────┬───────┘                                  │
│         │                                           │
│         ↓ db.query()                                │
│  ┌──────────────┐                                  │
│  │ SQLAlchemy   │                                  │
│  │ ORM          │                                  │
│  └──────┬───────┘                                  │
│         │                                           │
│         ↓ SQL Protocol                              │
└─────────┼───────────────────────────────────────────┘
          │ Port 5432
          ↓
┌─────────┼───────────────────────────────────────────┐
│ POSTGRESQL                                          │
│         ↓                                           │
│  SELECT * FROM users;                              │
│         ↓                                           │
│  [rows] → SQLAlchemy → FastAPI → React Query       │
└─────────────────────────────────────────────────────┘
```

### Exemple Complet : Lire des Utilisateurs

**1. Frontend : Composant React**

```tsx
// src/features/users/UsersList.tsx
import { useQuery } from '@tanstack/react-query'

function UsersList() {
  // React Query gère automatiquement:
  // - Le fetch
  // - Le cache (données gardées 5 min par défaut)
  // - Le loading state
  // - Les erreurs
  // - Le retry en cas d'échec

  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],  // Clé de cache unique
    queryFn: async () => {
      const response = await fetch('/api/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch users')
      }

      return response.json()
    },
    staleTime: 5 * 60 * 1000,  // 5 minutes
    retry: 3  // Retry 3 fois en cas d'échec
  })

  if (isLoading) return <div>Chargement...</div>
  if (error) return <div>Erreur: {error.message}</div>

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          {user.email} - Créé le {new Date(user.created_at).toLocaleDateString()}
        </li>
      ))}
    </ul>
  )
}
```

**2. Vite Proxy (Développement)**

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Ce qui se passe :**
```
1. React fait: fetch('/api/users')
2. Vite voit '/api' et transforme en: http://localhost:8000/api/users
3. FastAPI reçoit la requête
```

**3. Backend : Route FastAPI**

```python
# backend/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User
from auth import get_current_user

router = APIRouter(prefix="/api")

@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Vérifier les permissions
    if not current_user.has_permission('users:read'):
        raise HTTPException(403, "Permission refusée")

    # 2. Query la base via SQLAlchemy
    users = db.query(User).all()

    # 3. FastAPI convertit automatiquement en JSON
    # Grâce au modèle Pydantic (à définir)
    return users
```

**4. SQLAlchemy : Traduction en SQL**

```python
# Ce que fait db.query(User).all() en coulisse :

# 1. Construit la requête SQL
sql = """
    SELECT
        users.id,
        users.email,
        users.password_hash,
        users.created_at
    FROM users
"""

# 2. Exécute sur PostgreSQL
cursor.execute(sql)

# 3. Récupère les résultats
rows = cursor.fetchall()
# [
#   (UUID('123...'), 'marie@example.com', '$2b$12...', datetime(...)),
#   (UUID('456...'), 'paul@example.com', '$2b$12...', datetime(...))
# ]

# 4. Transforme en objets Python
users = []
for row in rows:
    user = User(
        id=row[0],
        email=row[1],
        password_hash=row[2],
        created_at=row[3]
    )
    users.append(user)

# 5. Retourne
return users
```

**5. Réponse JSON vers React**

```python
# FastAPI sérialise automatiquement:

[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "marie@example.com",
    "created_at": "2025-10-01T10:30:00"
    # password_hash est exclu par le modèle Pydantic
  },
  {
    "id": "456e4567-e89b-12d3-a456-426614174001",
    "email": "paul@example.com",
    "created_at": "2025-10-02T14:15:00"
  }
]
```

**6. React Query Cache et Affiche**

```tsx
// React Query met en cache avec la clé ['users']
// Si on fait un autre useQuery(['users']) dans 5 min,
// les données viennent du cache (pas de fetch)

// Ensuite, le composant affiche
```

---

## 5. Exemples Avancés : CRUD Complet

### Créer un Utilisateur (Mutation)

**Frontend :**

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

function CreateUserForm() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: async (data: { email: string, password: string }) => {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) throw new Error('Erreur création')

      return response.json()
    },
    onSuccess: () => {
      // Invalider le cache pour recharger la liste
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    mutation.mutate({
      email: formData.get('email') as string,
      password: formData.get('password') as string
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Création...' : 'Créer'}
      </button>
      {mutation.isError && <p>Erreur: {mutation.error.message}</p>}
      {mutation.isSuccess && <p>Utilisateur créé !</p>}
    </form>
  )
}
```

**Backend :**

```python
from pydantic import BaseModel, EmailStr
import bcrypt

class UserCreate(BaseModel):
    email: EmailStr
    password: str

@router.post("/users")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Vérifier permission
    if not current_user.has_permission('users:create'):
        raise HTTPException(403)

    # 2. Valider email unique
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(400, "Email déjà utilisé")

    # 3. Hasher le mot de passe
    password_hash = bcrypt.hashpw(
        user_data.password.encode(),
        bcrypt.gensalt()
    )

    # 4. Créer l'utilisateur
    new_user = User(
        email=user_data.email,
        password_hash=password_hash.decode()
    )

    # 5. Assigner le rôle par défaut
    default_role = db.query(Role).filter(Role.name == 'USER').first()
    new_user.roles.append(default_role)

    # 6. Sauvegarder
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Recharge l'ID généré

    # 7. Effets de bord
    send_welcome_email(new_user.email)
    log_audit('user_created', new_user.id, current_user.id)

    # 8. Retourner (sans password_hash)
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "created_at": new_user.created_at.isoformat()
    }
```

### Mettre à Jour un Utilisateur

**Frontend :**

```tsx
const updateMutation = useMutation({
  mutationFn: async ({ id, email }: { id: string, email: string }) => {
    const response = await fetch(`/api/users/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({ email })
    })
    return response.json()
  },
  onSuccess: (data, variables) => {
    // Mise à jour optimiste du cache
    queryClient.setQueryData(['users', variables.id], data)
    // Invalider la liste
    queryClient.invalidateQueries({ queryKey: ['users'] })
  }
})
```

**Backend :**

```python
class UserUpdate(BaseModel):
    email: EmailStr | None = None

@router.patch("/users/{user_id}")
def update_user(
    user_id: UUID,
    updates: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Récupérer l'utilisateur
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Utilisateur non trouvé")

    # Vérifier permission
    if not (current_user.id == user.id or current_user.has_permission('users:update')):
        raise HTTPException(403)

    # Appliquer les modifications
    if updates.email:
        user.email = updates.email

    db.commit()
    db.refresh(user)

    return {"id": str(user.id), "email": user.email}
```

---

## 6. Où Se Passent les Queries SQL ?

**Tableau récapitulatif :**

| Composant | Rôle | Fait des queries SQL ? | Protocole utilisé |
|-----------|------|------------------------|-------------------|
| **React** | Interface utilisateur | ❌ Non | - |
| **React Query** | Cache, state management | ❌ Non | - |
| **Vite** | Dev server, bundler | ❌ Non | HTTP (proxy) |
| **FastAPI** | API REST, logique métier | ✅ Oui (via SQLAlchemy) | HTTP (écoute) |
| **SQLAlchemy** | ORM Python ↔ SQL | ✅ Oui (génère SQL) | PostgreSQL Protocol |
| **PostgreSQL** | Base de données | ✅ Oui (exécute SQL) | PostgreSQL Protocol |

**Flux de données complet :**

```
┌──────────────────────────────────────────────────────────────┐
│ 1. USER INTERACTION                                          │
│    Utilisateur clique sur "Afficher les utilisateurs"        │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 2. REACT COMPONENT                                           │
│    useQuery(['users']) déclenche le fetch                    │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 3. REACT QUERY                                               │
│    Vérifie le cache → Pas de données → Appelle queryFn      │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 4. FETCH API                                                 │
│    fetch('/api/users')                                       │
│    GET /api/users HTTP/1.1                                   │
│    Authorization: Bearer eyJhbGc...                          │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 5. VITE PROXY                                                │
│    Intercepte /api → Redirige vers localhost:8000            │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 6. FASTAPI ROUTE                                             │
│    @router.get("/api/users")                                 │
│    - Décode JWT                                              │
│    - Vérifie permissions                                     │
│    - Appelle db.query(User).all()                            │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 7. SQLALCHEMY ORM                                            │
│    Construit le SQL:                                         │
│    SELECT users.id, users.email, users.created_at            │
│    FROM users                                                │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 8. POSTGRESQL                                                │
│    Exécute la requête                                        │
│    Retourne les rows:                                        │
│    [(uuid1, 'marie@...', datetime1),                         │
│     (uuid2, 'paul@...', datetime2)]                          │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 9. SQLALCHEMY (retour)                                       │
│    Transforme rows en objets User                            │
│    [User(id=uuid1, email='marie@...'), ...]                  │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 10. FASTAPI (retour)                                         │
│     Sérialise en JSON:                                       │
│     [{"id": "uuid1", "email": "marie@..."}, ...]             │
│     HTTP/1.1 200 OK                                          │
│     Content-Type: application/json                           │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 11. REACT QUERY (retour)                                     │
│     - Reçoit les données                                     │
│     - Met en cache avec clé ['users']                        │
│     - Update le state isLoading → false                      │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 12. REACT COMPONENT (retour)                                 │
│     Re-render avec data:                                     │
│     users.map(u => <li>{u.email}</li>)                       │
└────────────────────────┬─────────────────────────────────────┘
                         ↓
┌────────────────────────┴─────────────────────────────────────┐
│ 13. DOM UPDATE                                               │
│     Navigateur affiche:                                      │
│     • marie@example.com                                      │
│     • paul@example.com                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Pourquoi Cette Séparation Frontend/Backend ?

### Raison 1 : Sécurité

**Règle d'or :** Le frontend est **non fiable** (code exécuté chez l'utilisateur)

```tsx
// ❌ Faille de sécurité
function DeleteUser({ userId }: { userId: string }) {
  const isAdmin = localStorage.getItem('role') === 'admin'

  if (!isAdmin) return null  // Caché si pas admin

  return (
    <button onClick={() => fetch(`/api/users/${userId}`, { method: 'DELETE' })}>
      Supprimer
    </button>
  )
}

// Problème: Un utilisateur malveillant peut:
// 1. Ouvrir DevTools Console
// 2. Taper: fetch('/api/users/123', { method: 'DELETE' })
// 3. Le bouton n'apparaît pas, mais la requête est envoyée !
```

**Solution :** Vérification côté serveur **obligatoire**

```python
@router.delete("/users/{user_id}")
def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    # ✅ Vérification serveur (impossible à contourner)
    if not current_user.has_permission('users:delete'):
        raise HTTPException(403, "Permission refusée")

    # Seulement si autorisé
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
```

**Principe :** Frontend RBAC = UX (cacher les boutons), Backend RBAC = Sécurité (bloquer les actions)

### Raison 2 : Performance

**Cache React Query :**

```tsx
// Premier appel: fetch vers le serveur
const { data } = useQuery(['users'])  // → HTTP Request

// 5 secondes après, autre composant:
const { data } = useQuery(['users'])  // → Données du cache (instant)

// Pas de requête réseau, pas de query SQL
```

**Pool de Connexions SQLAlchemy :**

```python
# Sans pool:
# Chaque requête crée une nouvelle connexion TCP
# PostgreSQL accepte ~100 connexions max
# → Surcharge rapide

# Avec pool (SQLAlchemy):
engine = create_engine('postgresql://...', pool_size=10, max_overflow=20)

# 10 connexions persistantes réutilisées
# Max 30 connexions en pic (10 + 20 overflow)
# → Performance et scalabilité
```

### Raison 3 : Logique Métier Centralisée

**Exemple : Envoi d'email de bienvenue**

```python
# ✅ Côté serveur
@router.post("/users")
def create_user(...):
    user = User(...)
    db.add(user)
    db.commit()

    # Envoi email (serveur SMTP accessible)
    send_welcome_email(user.email)

    return user

# ❌ Impossible côté frontend
// Le navigateur ne peut pas se connecter à un serveur SMTP
// Même si on expose les credentials, c'est une faille de sécurité
```

**Exemple : Transaction multi-tables**

```python
@router.post("/orders")
def create_order(items: list[Item], db: Session = Depends(get_db)):
    # Transaction atomique
    try:
        # 1. Créer la commande
        order = Order(total=sum(i.price for i in items))
        db.add(order)

        # 2. Déduire du stock
        for item in items:
            product = db.query(Product).filter(Product.id == item.id).first()
            product.stock -= item.quantity

        # 3. Créer la facture
        invoice = Invoice(order_id=order.id)
        db.add(invoice)

        # Commit tout ou rien
        db.commit()
    except Exception:
        # Rollback si erreur
        db.rollback()
        raise
```

**Impossible côté frontend :** Le navigateur ne peut pas gérer des transactions SQL.

### Raison 4 : Réutilisabilité

**Même API utilisable par :**

```
┌─────────────┐
│ React Web   │────┐
└─────────────┘    │
                   ├──→ FastAPI /api/users
┌─────────────┐    │
│ Mobile App  │────┤
└─────────────┘    │
                   │
┌─────────────┐    │
│ CLI Tool    │────┘
└─────────────┘
```

**Exemple : CLI Python**

```python
import requests

response = requests.get('http://localhost:8000/api/users', headers={
    'Authorization': f'Bearer {token}'
})

users = response.json()
for user in users:
    print(user['email'])
```

**Même logique métier, mêmes permissions, même base de données.**

---

## 8. Résumé : Architecture Moderne du Web

### Stack Complète

```
┌──────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER (Frontend)                            │
│                                                          │
│  React + TypeScript                                      │
│  ├─ Components (UI)                                      │
│  ├─ React Query (State management serveur)              │
│  ├─ Context (State local: permissions, user)            │
│  └─ Vite (Dev server, bundler)                          │
│                                                          │
│  Protocole: HTTP/HTTPS                                   │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────┴───────────────────────────────────────┐
│ APPLICATION LAYER (Backend)                              │
│                                                          │
│  FastAPI + Python                                        │
│  ├─ Routes (Endpoints REST)                              │
│  ├─ Dependencies (Auth, DB session)                      │
│  ├─ Pydantic (Validation)                                │
│  └─ Business Logic (Logique métier)                      │
│                                                          │
│  Protocole: PostgreSQL Wire Protocol                     │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────┴───────────────────────────────────────┐
│ DATA LAYER (Database)                                    │
│                                                          │
│  PostgreSQL                                              │
│  ├─ Tables (users, roles, permissions)                   │
│  ├─ Indexes (Performance)                                │
│  ├─ Constraints (Intégrité)                              │
│  └─ Triggers (Logique DB)                                │
└──────────────────────────────────────────────────────────┘
```

### Flux de Données : Diagramme Simplifié

```
USER ACTION
    ↓
React Component
    ↓
React Query (cache check)
    ↓
fetch() HTTP
    ↓
FastAPI Route
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL
    ↓
Rows
    ↓
SQLAlchemy (objets Python)
    ↓
FastAPI (JSON)
    ↓
React Query (cache + state)
    ↓
Component (render)
    ↓
DOM Update
    ↓
USER SEES RESULT
```

### Points Clés à Retenir

**1. React ne peut JAMAIS parler directement à PostgreSQL**
- Limitations du navigateur (sandbox)
- Protocole incompatible
- Sécurité (credentials)

**2. FastAPI est OBLIGATOIRE comme couche intermédiaire**
- Traduction HTTP ↔ SQL
- Sécurité (JWT, permissions)
- Logique métier

**3. Vite ne remplace PAS FastAPI**
- Vite = build tool frontend
- FastAPI = application server backend
- Vite proxy = redirection HTTP (dev uniquement)

**4. React Query optimise la communication**
- Cache intelligent
- Retry automatique
- State management serveur

**5. SQLAlchemy traduit Python ↔ SQL**
- ORM (Object-Relational Mapping)
- Query builder
- Pool de connexions

**Cette architecture est le standard du web moderne**, utilisée par des millions d'applications (Airbnb, Uber, etc.)
