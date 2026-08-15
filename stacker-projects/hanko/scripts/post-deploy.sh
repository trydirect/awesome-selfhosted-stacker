#!/bin/bash
set -euo pipefail

echo "Generating Hanko config on server..."

# Read DB_PASSWORD from .env
DB_PASSWORD=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
SECRETS_DEFAULT=$(grep "^SECRETS_DEFAULT=" .env | cut -d= -f2-)

# Create config.yaml on the server
ssh -i ~/.config/stacker/ssh/server-391_ed25519 root@62.238.110.174 "cat > /home/trydirect/project/config.yaml << 'EOFCONFIG'
server:
  port: 8000
  public_port: 8000
  env: production
  webauthn:
    relying_party:
      id: localhost
database:
  host: hanko-db
  port: 5432
  user: hanko
  password: ${DB_PASSWORD}
  database: hanko
  dialect: postgres
secrets:
  default: ${SECRETS_DEFAULT}
EOFCONFIG

# Substitute actual values
sed -i 's|\${DB_PASSWORD}|${DB_PASSWORD}|g' /home/trydirect/project/config.yaml
sed -i 's|\${SECRETS_DEFAULT}|${SECRETS_DEFAULT}|g' /home/trydirect/project/config.yaml

# Run migrations
docker run --rm \\
  --network project_app-network \\
  -v /home/trydirect/project/config.yaml:/etc/config.yaml:ro \\
  ghcr.io/teamhanko/hanko:latest migrate up --config /etc/config.yaml

# Restart the app
docker restart project-app-1

echo "Hanko config and migrations complete."
