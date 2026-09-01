# etherpad — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-22
**Focus:** `proxy.type: nginx` + `stacker secrets` (per session theme)

## Setup / commands

```bash
cd stacker-projects/etherpad
# creds via stacker secrets (local .env mode)
stacker secrets set "ETHERPAD_ADMIN_PASSWORD=$(openssl rand -hex 16)"
stacker secrets set "ETHERPAD_USER_PASSWORD=$(openssl rand -hex 16)"
stacker secrets validate     # ✓ both refs resolved
stacker deploy --target local
```

Two `stacker.yml` edits were needed first (see `BUGS.md`):
1. Added `env_file: .env` + a `proxy.type: nginx` block (project had neither).
2. Removed invalid `socketIo: {}` / `logconfig: {}` env entries (maps, not
   strings — stacker correctly refused to parse them).

## Verification

- `docker ps` → `stacker-app-1` (etherpad/etherpad:latest) up on 9001,
  plus `stacker-nginx-1` (the proxy) on 80/443.
- App **direct**: `curl http://localhost:9001/` → `200`; `/admin/` → `200`;
  `/p/stacker-test` (pad) → `200`. Etherpad is fully functional.
- Secrets: `stacker secrets set/validate` worked; `ADMIN_PASSWORD` /
  `USER_PASSWORD` rendered into `.stacker/docker-compose.yml` correctly.

## Proxy finding (stacker#242 — nginx also a no-op)

Through the nginx proxy: `curl -H "Host: etherpad.example.com"
http://localhost:80/` → `000`. Root cause: stacker mounts
`./nginx/conf.d` but generates **no config** into it (empty dir), so nginx
has no vhost/upstream for the app. Same bug as traefik — confirmed and
added to [stacker#242](https://github.com/trydirect/stacker/issues/242)
(the proxy-config generation is unimplemented for `nginx` as well as
`traefik`). Not an etherpad-specific issue.

## Result

stacker-level PASS: app deploys and runs, secrets management works. The
proxy is inert (#242) — verify apps on their **direct** published port,
not via the proxy domain.
