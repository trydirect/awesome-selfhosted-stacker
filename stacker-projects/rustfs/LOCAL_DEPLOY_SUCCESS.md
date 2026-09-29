# rustfs — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): empty `config_contract` service block → volume
policies (`rustfs_data`, `rustfs_logs`).

## Verification

| Check | Result |
|---|---|
| Containers | `rustfs-app-1` Up (9000/9001), `rustfs-otel-collector-1` Up (survives with empty config) |
| S3 API `GET /` (:9000) | `AccessDenied` XML — correct S3 semantics (auth enforced) |
| Console (:9001) | 403 unauthenticated (JS/token login — not curl-testable) |

## Notes

Verification for S3 stores is "correct auth-denial responses", like kopia's 401.
Console requires a browser session with `RUSTFS_ACCESS_KEY`/`RUSTFS_SECRET_KEY`.
