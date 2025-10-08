#!/bin/bash
# Complete setup script for the application

echo "========================================"
echo "Template WebApp - Setup Script"
echo "========================================"
echo ""

# Wait for services to be ready
echo "Waiting for services..."
sleep 5

# Initialize PostgreSQL database
echo ""
echo "Initializing PostgreSQL database..."
python scripts/init_db.py

if [ $? -ne 0 ]; then
    echo "Failed to initialize database"
    exit 1
fi

# Initialize RDF dataset
echo ""
echo "Initializing RDF dataset..."
python scripts/init_rdf.py

if [ $? -ne 0 ]; then
    echo "Failed to initialize RDF dataset"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "Access points:"
echo "  - Frontend: http://localhost:5173"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Fuseki UI: http://localhost:3030"
echo ""
echo "Default credentials:"
echo "  - Admin: admin / admin"
echo "  - Demo: demo / demo"
echo ""
