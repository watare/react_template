#!/bin/bash
# Script de test pour vérifier que l'application fonctionne

echo "======================================"
echo "Test de l'application Template WebApp"
echo "======================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Services Docker
echo "1. Vérification des services Docker..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Services Docker actifs"
else
    echo -e "${RED}✗${NC} Services Docker non actifs"
    echo "   Lancez: docker-compose up -d"
    exit 1
fi

# Test 2: PostgreSQL
echo ""
echo "2. Test PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} PostgreSQL opérationnel"

    # Vérifier que les users existent
    USER_COUNT=$(docker-compose exec -T postgres psql -U postgres -d template_db -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')
    if [ "$USER_COUNT" -ge "2" ]; then
        echo -e "${GREEN}✓${NC} Utilisateurs créés ($USER_COUNT users)"
    else
        echo -e "${YELLOW}⚠${NC} Base de données vide ou en cours d'initialisation"
    fi
else
    echo -e "${RED}✗${NC} PostgreSQL non accessible"
    exit 1
fi

# Test 3: Fuseki
echo ""
echo "3. Test Fuseki..."
if curl -s http://localhost:3030/$/ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Fuseki opérationnel"

    # Vérifier dataset
    if curl -s http://localhost:3030/\$/datasets | grep -q "template_dataset"; then
        echo -e "${GREEN}✓${NC} Dataset RDF créé"
    else
        echo -e "${YELLOW}⚠${NC} Dataset en cours de création"
    fi
else
    echo -e "${RED}✗${NC} Fuseki non accessible"
    exit 1
fi

# Test 4: Backend API
echo ""
echo "4. Test Backend API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend API actif"

    # Test login
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=admin&password=admin" 2>/dev/null)

    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        echo -e "${GREEN}✓${NC} Login admin fonctionne"
    else
        echo -e "${YELLOW}⚠${NC} Login échoue - Vérifier l'initialisation"
        echo "   Response: $LOGIN_RESPONSE"
    fi
else
    echo -e "${RED}✗${NC} Backend API non accessible"
    echo "   Vérifier: docker-compose logs backend"
    exit 1
fi

# Test 5: Frontend
echo ""
echo "5. Test Frontend..."
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend accessible"
else
    echo -e "${RED}✗${NC} Frontend non accessible"
    exit 1
fi

# Résumé
echo ""
echo "======================================"
echo -e "${GREEN}✓ Tous les tests sont passés !${NC}"
echo "======================================"
echo ""
echo "Accès:"
echo "  Frontend:  http://localhost:5173"
echo "  API:       http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Fuseki:    http://localhost:3030"
echo ""
echo "Identifiants:"
echo "  Admin: admin / admin"
echo "  Demo:  demo / demo"
echo ""
