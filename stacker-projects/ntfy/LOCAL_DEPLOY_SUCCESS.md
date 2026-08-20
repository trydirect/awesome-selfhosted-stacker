# ntfy — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-19

## Commands used

```bash
cd stacker-projects/ntfy
cp .env.example .env
./scripts/generate-secrets.sh
stacker deploy --target local
```

`deploy.target` in `stacker.yml` is `server`; `--target local` overrides it
without modifying the file.

## Verification

- `docker ps` shows `stacker-app-1` (binwiederhier/ntfy:latest) up, port
  `0.0.0.0:8080->80/tcp`.
- `curl -I http://localhost:8080/` → `HTTP/1.1 200 OK`
- `curl http://localhost:8080/v1/health` → `{"healthy":true}`
- Publish: `curl -d "hello from stacker test" http://localhost:8080/mytopic`
  → message accepted, returned message id.
- Read back: `curl "http://localhost:8080/mytopic/json?poll=1"` → returned
  the same message, confirming the ntfy pub/sub core function works.

No stacker or ntfy bugs encountered.
