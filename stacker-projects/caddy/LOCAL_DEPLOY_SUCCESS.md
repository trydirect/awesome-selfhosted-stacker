# caddy — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-20

## Commands used

```bash
cd stacker-projects/caddy
chmod +x scripts/generate-secrets.sh   # script wasn't executable in the repo checkout
./scripts/generate-secrets.sh
stacker deploy --target local
```

Note: `./scripts/generate-secrets.sh` failed with "permission denied" before
`chmod +x` — the script lost its executable bit somewhere. stacker itself
handled the missing `.env` gracefully anyway (auto-created it from
`.env.example` with a log line), so this wasn't blocking, just noted here.

## Verification

- `docker ps` → `stacker-app-1` (caddy:latest) up, ports `80`, `443/tcp`,
  `443/udp` all bound.
- `curl -I http://localhost/` → `HTTP/1.1 200 OK`, serving Caddy's default
  welcome page.
- `docker logs stacker-app-1` → clean startup: config loaded from
  Caddyfile, HTTP server running on `:80` (HTTPS correctly skipped since
  no TLS-capable domain configured locally — expected for `localhost`).

No stacker or caddy bugs found.
