"""
Initialize database with tables and seed data
"""
import sys
sys.path.append('/app')

from app.db.base import Base, engine
from app.models.user import User, Role, Permission
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_permissions(db: Session):
    """Create default permissions"""
    print("Creating permissions...")

    permissions_data = [
        {"code": "nodes:read", "name": "Read Nodes", "description": "View RDF nodes"},
        {"code": "nodes:write", "name": "Write Nodes", "description": "Create and update RDF nodes"},
        {"code": "nodes:delete", "name": "Delete Nodes", "description": "Delete RDF nodes"},
        {"code": "users:read", "name": "Read Users", "description": "View users"},
        {"code": "users:write", "name": "Write Users", "description": "Create and update users"},
        {"code": "users:delete", "name": "Delete Users", "description": "Delete users"},
        {"code": "admin", "name": "Admin Access", "description": "Full system access"},
    ]

    for perm_data in permissions_data:
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            print(f"  ✓ Created permission: {perm_data['code']}")

    db.commit()
    print("✓ Permissions created successfully")


def seed_roles(db: Session):
    """Create default roles"""
    print("Creating roles...")

    # Admin role - all permissions
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if not admin_role:
        admin_role = Role(
            name="Admin",
            description="Administrator with full access"
        )
        all_permissions = db.query(Permission).all()
        admin_role.permissions = all_permissions
        db.add(admin_role)
        print("  ✓ Created role: Admin")

    # Viewer role - read-only
    viewer_role = db.query(Role).filter(Role.name == "Viewer").first()
    if not viewer_role:
        viewer_role = Role(
            name="Viewer",
            description="Read-only access"
        )
        read_permissions = db.query(Permission).filter(
            Permission.code.in_(["nodes:read", "users:read"])
        ).all()
        viewer_role.permissions = read_permissions
        db.add(viewer_role)
        print("  ✓ Created role: Viewer")

    # Editor role - read and write (no delete)
    editor_role = db.query(Role).filter(Role.name == "Editor").first()
    if not editor_role:
        editor_role = Role(
            name="Editor",
            description="Can read and write data"
        )
        editor_permissions = db.query(Permission).filter(
            Permission.code.in_(["nodes:read", "nodes:write", "users:read"])
        ).all()
        editor_role.permissions = editor_permissions
        db.add(editor_role)
        print("  ✓ Created role: Editor")

    db.commit()
    print("✓ Roles created successfully")


def seed_users(db: Session):
    """Create default users"""
    print("Creating users...")

    # Admin user
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin"),
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
            hashed_password=get_password_hash("demo"),
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


def main():
    """Main initialization function"""
    print("\n" + "="*50)
    print("Database Initialization Script")
    print("="*50 + "\n")

    try:
        # Create tables
        create_tables()

        # Create session
        from app.db.base import SessionLocal
        db = SessionLocal()

        try:
            # Seed data
            seed_permissions(db)
            seed_roles(db)
            seed_users(db)

            print("\n" + "="*50)
            print("✓ Database initialized successfully!")
            print("="*50)
            print("\nDefault credentials:")
            print("  Admin: admin / admin")
            print("  Demo:  demo / demo")
            print("")

        finally:
            db.close()

    except Exception as e:
        print(f"\n✗ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
