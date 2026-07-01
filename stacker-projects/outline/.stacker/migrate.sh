#!/bin/sh
set -e

# Run database migrations inside the running app container.
# This hook runs AFTER the containers are up (local deployment only).
# For cloud deployments, migrations run via the container's own CMD (entrypoint.sh).
if [ -f .stacker/docker-compose.yml ]; then
  echo "Running database migrations inside app container..."
  docker compose -f .stacker/docker-compose.yml exec -T app npx sequelize db:migrate --env=production-ssl-disabled
  echo "Migrations complete."
else
  echo "No local compose file found; skipping host-side migrations (they run on container start for cloud deploys)."
fi
