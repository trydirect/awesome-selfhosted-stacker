# [FIXED] teable backend listens on :3002, not :3000 (connection reset)

## Status: FIXED / VERIFIED

## Summary
teable's split-stack template mapped host 3000 -> container 3000, but the old
image put the Next.js frontend on :3002 and Nest backend on :3001, so HTTP got
`connection reset` on the mapped port.

## Resolution (2026-10-11)
- Switched to the official all-in-one image `ghcr.io/teableio/teable:latest`,
  which serves the UI + API on container port 3000 (`3000:3000`).
- Added a `redis` service (required by the all-in-one).
- Set `PRISMA_DATABASE_URL`, `BACKEND_CACHE_*`, `PUBLIC_ORIGIN`.
- Switched db to `postgres:16-alpine` (volume held v16 data; v15 was
  incompatible).

Result: HTTP 307 → 200 on `/auth/signup`. See `LOCAL_DEPLOY_SUCCESS.md`.

## Environment
- Test server: 46.224.127.228
- Deployments: #1345, #1346
