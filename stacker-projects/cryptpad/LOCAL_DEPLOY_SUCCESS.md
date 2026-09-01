# cryptpad — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-20

## Commands used

```bash
cd stacker-projects/cryptpad
./scripts/generate-secrets.sh
stacker deploy --target local
```

Same `env_file` gap as `code-server` — `stacker.yml` had no `env_file:`
key, so `${DOMAIN}` substitution would have failed. Fixed by adding
`env_file: .env`. See `BUGS.md`.

## Verification

- `docker ps` → `stacker-app-1` (cryptpad/cryptpad:latest) up,
  `0.0.0.0:3000-3001->3000-3001/tcp`, Docker healthcheck reports `healthy`.
- `curl -I http://localhost:3000/` → `HTTP/1.1 200 OK`

No remaining bugs blocking local deploy once `env_file` was added.
