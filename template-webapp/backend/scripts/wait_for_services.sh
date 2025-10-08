#!/bin/bash
# Wait for PostgreSQL and Fuseki to be ready

echo "Waiting for PostgreSQL..."
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is up!"

echo "Waiting for Fuseki..."
until curl -f http://fuseki:3030/$/ping > /dev/null 2>&1; do
  echo "Fuseki is unavailable - sleeping"
  sleep 2
done
echo "Fuseki is up!"

echo "All services are ready!"
