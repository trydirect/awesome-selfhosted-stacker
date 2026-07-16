#!/bin/bash
set -e

# Fix missing passwords for Supabase internal users.
# The supabase/postgres image creates these roles but does not always set
# their passwords to match POSTGRES_PASSWORD. This script runs last in the
# init sequence and ensures the connection strings used by Auth, REST and
# Storage can authenticate.
#
# DB_INIT_PASSWORD is injected by stacker.yml so the literal value is not
# expanded during the Stacker config-bundle phase.
PASS="${DB_INIT_PASSWORD:-$POSTGRES_PASSWORD}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    ALTER USER authenticator WITH PASSWORD '$PASS';
    ALTER USER supabase_auth_admin WITH PASSWORD '$PASS';
    ALTER USER supabase_storage_admin WITH PASSWORD '$PASS';
EOSQL
