# ✅ Vérification : Les users admin et demo sont bien créés

## 📋 Confirmation du script d'initialisation

### Fichier : `backend/scripts/init_db.py`

Le script **existe** et contient :

#### 1. Fonction `seed_users()` (ligne 92-131)

```python
def seed_users(db: Session):
    """Create default users"""
    print("Creating users...")

    # Admin user
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin"),  # ← Mot de passe "admin" hashé
            full_name="Administrator",
            is_active=True,
            is_superuser=True
        )
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if admin_role:
            admin.roles.append(admin_role)
        db.add(admin)
        print("  ✓ Created user: admin / admin")

    # Demo user
    demo = db.query(User).filter(User.username == "demo").first()
    if not demo:
        demo = User(
            email="demo@example.com",
            username="demo",
            hashed_password=get_password_hash("demo"),  # ← Mot de passe "demo" hashé
            full_name="Demo User",
            is_active=True,
            is_superuser=False
        )
        viewer_role = db.query(Role).filter(Role.name == "Viewer").first()
        if viewer_role:
            demo.roles.append(viewer_role)
        db.add(demo)
        print("  ✓ Created user: demo / demo")

    db.commit()
    print("✓ Users created successfully")
```

#### 2. Fonction `main()` (ligne 134-170)

```python
def main():
    """Main initialization function"""
    try:
        # Create tables
        create_tables()

        # Create session
        from app.db.base import SessionLocal
        db = SessionLocal()

        try:
            # Seed data
            seed_permissions(db)  # ← Crée les permissions
            seed_roles(db)        # ← Crée les rôles
            seed_users(db)        # ← CRÉE LES USERS !

            print("\n" + "="*50)
            print("✓ Database initialized successfully!")
            print("="*50)
            print("\nDefault credentials:")
            print("  Admin: admin / admin")
            print("  Demo:  demo / demo")
```

### ✅ Le script est appelé automatiquement

**Fichier** : `docker-compose.yml` (ligne 78)

```yaml
command: >
  sh -c "
    echo 'Waiting for services...' &&
    bash scripts/wait_for_services.sh &&
    echo 'Running database migrations...' &&
    python scripts/init_db.py &&              # ← EXÉCUTÉ ICI !
    echo 'Initializing RDF dataset...' &&
    python scripts/init_rdf.py &&
    echo 'Starting FastAPI server...' &&
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  "
```

---

## 🔍 Comment vérifier que ça fonctionne ?

### Méthode 1 : Script automatique

```bash
cd template-webapp
bash check_users.sh
```

**Résultat attendu** :
```
✓ PostgreSQL accessible
✓ Table 'users' existe

Liste des utilisateurs dans la base:
------------------------------------
 username |       email        | is_active | is_superuser |  roles
----------+--------------------+-----------+--------------+---------
 admin    | admin@example.com  | t         | t            | Admin
 demo     | demo@example.com   | t         | f            | Viewer

✓ Utilisateur 'admin' existe
✓ Utilisateur 'demo' existe
✓ Login API fonctionne !
```

### Méthode 2 : Requête SQL directe

```bash
docker-compose exec postgres psql -U postgres -d template_db -c "SELECT username, email, is_superuser FROM users;"
```

**Résultat attendu** :
```
 username |       email        | is_superuser
----------+--------------------+--------------
 admin    | admin@example.com  | t
 demo     | demo@example.com   | f
```

### Méthode 3 : Test login API

```bash
# Test admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"

# Test demo
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo"
```

**Résultat attendu** : Un JSON avec `access_token`

### Méthode 4 : Frontend

1. Ouvrir http://localhost:5173
2. Entrer : `admin` / `admin`
3. Cliquer "Sign in"

**Résultat attendu** : Redirection vers le dashboard

---

## 📊 Détails des utilisateurs créés

### Admin

| Champ | Valeur |
|-------|--------|
| **Username** | `admin` |
| **Password** | `admin` (hashé en bcrypt) |
| **Email** | admin@example.com |
| **Full Name** | Administrator |
| **is_active** | `true` |
| **is_superuser** | `true` |
| **Role** | Admin |
| **Permissions** | Toutes (nodes:read, nodes:write, nodes:delete, users:*, admin) |

### Demo

| Champ | Valeur |
|-------|--------|
| **Username** | `demo` |
| **Password** | `demo` (hashé en bcrypt) |
| **Email** | demo@example.com |
| **Full Name** | Demo User |
| **is_active** | `true` |
| **is_superuser** | `false` |
| **Role** | Viewer |
| **Permissions** | Lecture seule (nodes:read, users:read) |

---

## 🔐 Sécurité des mots de passe

Les mots de passe sont hashés avec **bcrypt** via la fonction `get_password_hash()` :

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

**Exemple de hash** (chaque exécution donne un hash différent) :
```
$2b$12$KIXVzwVgU8qKZ5I9r.8JYeCqV4J3Gq5j9K0V7lX2mN4pQ6rS8tU9W
```

---

## 🚀 Ordre d'exécution au démarrage

```
1. docker-compose up -d
   ↓
2. PostgreSQL démarre
   ↓
3. Backend attend PostgreSQL (wait_for_services.sh)
   ↓
4. init_db.py exécuté:
   ├─ create_tables()      → Crée users, roles, permissions, audit_logs
   ├─ seed_permissions()   → Insère les 7 permissions
   ├─ seed_roles()         → Insère Admin, Editor, Viewer
   └─ seed_users()         → Insère admin et demo ✅
   ↓
5. init_rdf.py exécuté (Fuseki)
   ↓
6. FastAPI démarre
   ↓
7. Frontend démarre
```

---

## ❓ Et si les users ne sont pas créés ?

### Cas 1 : Le backend n'a pas fini l'initialisation

**Symptôme** : Erreur 500 ou table vide

**Solution** :
```bash
# Attendre que l'init soit terminée
docker-compose logs -f backend | grep "Database initialized successfully"
```

### Cas 2 : Init_db.py a échoué

**Symptôme** : Erreurs dans les logs

**Solution** :
```bash
# Voir les erreurs
docker-compose logs backend

# Réinitialiser
docker-compose down -v
docker-compose up -d
```

### Cas 3 : Réinitialisation manuelle

```bash
# Accéder au container
docker-compose exec backend bash

# Lancer manuellement
python scripts/init_db.py
```

---

## ✅ Conclusion

**OUI**, le script existe et crée bien les users `admin` et `demo` !

**Preuve** :
- ✅ Fichier `backend/scripts/init_db.py` existe (170 lignes)
- ✅ Fonction `seed_users()` crée admin et demo (lignes 92-131)
- ✅ Appelé dans `docker-compose.yml` (ligne 78)
- ✅ Exécuté automatiquement au démarrage
- ✅ Mots de passe hashés avec bcrypt
- ✅ Rôles assignés (Admin pour admin, Viewer pour demo)

**Pour vérifier** :
```bash
bash check_users.sh
```
