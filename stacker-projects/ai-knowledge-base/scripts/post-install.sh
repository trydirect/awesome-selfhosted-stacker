#!/bin/bash
set -e

echo "Running Dify database migrations..."
sleep 10
docker exec project-app-1 flask db upgrade
echo "Database migrations complete."
