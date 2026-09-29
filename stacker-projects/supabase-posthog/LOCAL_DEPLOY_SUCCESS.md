# supabase-posthog — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

10/10 services Up; `rest/v1/` → **200**; posthog receiver :8001 → **200**.

## Fixture fixes applied (supabase lessons — see BUGS.md)

1. `postgresql.schema.sql` generation + mount (role passwords incl.
   `supabase_storage_admin`; + `graphql_public` + auth-function ownership).
2. `DB_ENC_KEY: supabaserealtime` → `${DB_ENC_KEY}` (16-byte AES-128 key).
3. Bind staging into `.stacker/` (`kong.yml`, `posthog-receiver/`,
   `postgresql.schema.sql`) — including removing Docker-created *directories*
   masquerading as the file binds before copying.
4. `ssh_key` hardcoded path normalized (server leg).

## Verification

| Check | Result |
|---|---|
| Containers | 10/10 Up |
| Kong `rest/v1/`, `auth/v1/health` | **200** / **200** |
| posthog receiver :8001 | **200** |
