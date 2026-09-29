# supabase — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

All 10 services Up: app (kong), db, studio, auth, rest, realtime, storage,
imgproxy, meta, functions. `rest/v1/` → **200**, `auth/v1/health` → **200**.

## Fixture fixes applied (see `BUGS.md`)

1. **`postgresql.schema.sql` mount + generation** — role passwords (`authenticator`,
   `supabase_auth_admin`, `supabase_functions_admin`, `supabase_storage_admin`) are
   set ONLY via `/etc/postgresql.schema.sql` post-init hook; the template never
   mounted it. Generator now writes the file from `.env` and the db service mounts
   it (`./postgresql.schema.sql:/etc/postgresql.schema.sql:ro`).
2. **Contract-key syncs (~15 keys)** — every contract-`generated` field becomes a
   `${KEY}` placeholder needing an equally-named `.env` entry. All role passwords
   intentionally share `POSTGRES_PASSWORD` (template design); JWT-family keys share
   `JWT_SECRET`; `SUPABASE_*` keys alias `ANON_KEY`/`SERVICE_ROLE_KEY`.
3. **`DB_ENC_KEY` must be 16 chars** — `Realtime.Crypto` uses `:aes_128_ecb`
   ("Bad key size" crash otherwise). Template had 14-char `supabaserealtime`.
4. **auth schema ownership** — gotrue's migrations `CREATE OR REPLACE` functions
   (`auth.uid()` etc.) owned by init-schema: `ALTER ... OWNER TO supabase_auth_admin`
   for all `auth` schema functions (one-time).
5. **`graphql_public` schema** — postgrest loads `db-schemas=public,storage,graphql_public`;
   created the missing schema (one-time).
6. **edge-runtime command** — `command: start --main-service /home/deno/functions/main
   --port 8081` (default CMD prints help; v1.74 rejects `--hostname`).
7. **Bind staging** — `./volumes/functions` staged into `.stacker/` (bind class);
   `kong.yml` + `postgresql.schema.sql` likewise.

## Verification

| Check | Result |
|---|---|
| Containers | 10/10 Up (db healthy, meta healthy, studio healthy) |
| Kong `rest/v1/` | **200** |
| Kong `auth/v1/health` | **200** |
| `storage/v1/object`, `functions/v1` | 404 (expected without auth/function name) |
| `realtime/v1/health` | 404 (no such route in realtime 2.102; service Up) |
