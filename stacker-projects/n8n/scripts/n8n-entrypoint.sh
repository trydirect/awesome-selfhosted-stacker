#!/bin/sh
# Mounted over the image's /docker-entrypoint.sh. Sets the instance owner from
# ADMIN_EMAIL / ADMIN_PASSWORD before n8n starts: an n8n without an owner lets
# whoever opens it first create one, and N8N_INSTANCE_OWNER_PASSWORD_HASH only
# accepts a bcrypt hash, which a deploy form cannot generate.
set -e

if [ -z "${ADMIN_EMAIL:-}" ] || [ -z "${ADMIN_PASSWORD:-}" ]; then
  echo "n8n-entrypoint: ADMIN_EMAIL and ADMIN_PASSWORD must be set;" \
    "refusing to start an n8n anyone could claim" >&2
  exit 1
fi

N8N_INSTANCE_OWNER_PASSWORD_HASH=$(cd /usr/local/lib/node_modules/n8n && node -e \
  'process.stdout.write(require("bcryptjs").hashSync(process.env.ADMIN_PASSWORD, 10))')
export N8N_INSTANCE_OWNER_MANAGED_BY_ENV=true
export N8N_INSTANCE_OWNER_EMAIL="$ADMIN_EMAIL"
export N8N_INSTANCE_OWNER_PASSWORD_HASH
unset ADMIN_PASSWORD

# The rest is the image's own entrypoint.
if [ -d /opt/custom-certificates ]; then
  echo "Trusting custom certificates from /opt/custom-certificates."
  export NODE_OPTIONS="--use-openssl-ca $NODE_OPTIONS"
  export SSL_CERT_DIR=/opt/custom-certificates
  c_rehash /opt/custom-certificates
fi

if [ "$#" -gt 0 ]; then
  exec n8n "$@"
else
  exec n8n
fi
