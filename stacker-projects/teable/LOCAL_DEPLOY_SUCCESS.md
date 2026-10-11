# Teable — Local Deploy Success

## Result: SUCCESS

- **Image:** `ghcr.io/teableio/teable:latest` (all-in-one)
- **Host port:** 3000
- **Deployments:** #1345, #1346
- **Verified:** HTTP 307 → 200 on `/auth/signup`

## Fix applied

Replaced the split-stack template with the official all-in-one image, which
serves the web UI and API on container port 3000:
- `image: ghcr.io/teableio/teable:latest`, map `3000:3000`.
- Added a `redis` service (`redis-server --appendonly yes --requirepass ...`).
- Set `PRISMA_DATABASE_URL`, `BACKEND_CACHE_*`, `PUBLIC_ORIGIN` env.
- Switched db image to `postgres:16-alpine` — the named volume held v16 data
  and postgres:15 failed with "database files are incompatible".

## Commands used
```bash
cd stacker-projects/teable
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test --force-rebuild
```

## Verification
- `curl -o /dev/null -w "%{http_code}" -L http://46.224.127.228:3000/auth/signup` → `200`.
- Page title contains "Sign up" / "teable".

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-11
