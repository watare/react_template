#!/bin/bash
# Script pour vérifier que les utilisateurs admin et demo existent

echo "======================================"
echo "Vérification des utilisateurs"
echo "======================================"
echo ""

# Vérifier que PostgreSQL est accessible
if ! docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "❌ PostgreSQL n'est pas accessible"
    echo "   Lancez d'abord: docker-compose up -d"
    exit 1
fi

echo "✓ PostgreSQL accessible"
echo ""

# Vérifier que la table users existe
echo "Vérification de la table 'users'..."
TABLE_CHECK=$(docker-compose exec -T postgres psql -U postgres -d template_db -t -c "\dt users" 2>/dev/null)
if [ -z "$TABLE_CHECK" ]; then
    echo "❌ Table 'users' n'existe pas"
    echo "   Le backend n'a pas encore initialisé la base"
    echo "   Attendez que l'initialisation se termine"
    exit 1
fi
echo "✓ Table 'users' existe"
echo ""

# Lister tous les utilisateurs
echo "Liste des utilisateurs dans la base:"
echo "------------------------------------"
docker-compose exec -T postgres psql -U postgres -d template_db -c "
SELECT
    username,
    email,
    is_active,
    is_superuser,
    (SELECT string_agg(r.name, ', ') FROM roles r
     JOIN user_roles ur ON r.id = ur.role_id
     WHERE ur.user_id = users.id) as roles
FROM users;" 2>/dev/null

echo ""

# Vérifier admin
echo "Vérification utilisateur 'admin':"
ADMIN_EXISTS=$(docker-compose exec -T postgres psql -U postgres -d template_db -t -c "SELECT username FROM users WHERE username='admin';" 2>/dev/null | tr -d ' \n')
if [ "$ADMIN_EXISTS" = "admin" ]; then
    echo "  ✓ Utilisateur 'admin' existe"
    echo "  ✓ Mot de passe: admin"
    echo "  ✓ Login: curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin&password=admin'"
else
    echo "  ❌ Utilisateur 'admin' n'existe pas"
fi
echo ""

# Vérifier demo
echo "Vérification utilisateur 'demo':"
DEMO_EXISTS=$(docker-compose exec -T postgres psql -U postgres -d template_db -t -c "SELECT username FROM users WHERE username='demo';" 2>/dev/null | tr -d ' \n')
if [ "$DEMO_EXISTS" = "demo" ]; then
    echo "  ✓ Utilisateur 'demo' existe"
    echo "  ✓ Mot de passe: demo"
    echo "  ✓ Login: curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=demo&password=demo'"
else
    echo "  ❌ Utilisateur 'demo' n'existe pas"
fi
echo ""

# Test de connexion réel
echo "Test de connexion API:"
echo "------------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin" 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✓ Login API fonctionne !"
    echo "✓ Token reçu"
else
    echo "❌ Login API échoue"
    echo "Response: $LOGIN_RESPONSE"
fi
echo ""

echo "======================================"
echo "Vérification terminée"
echo "======================================"
