#!/bin/sh
set -e

echo "Running database migrations..."
npx sequelize db:migrate --env=production-ssl-disabled

echo "Starting Outline server..."
exec node build/server/index.js
