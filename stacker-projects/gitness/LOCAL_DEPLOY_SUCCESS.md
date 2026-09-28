# gitness — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed.

## Commands

```bash
cd stacker-projects/gitness
./scripts/generate-secrets.sh
set -a; source ../../.env; set +a
stacker config validate && stacker deploy --target local
```

## Verification

| Check | Result |
|---|---|
| Container | `gitness-app-1` Up, `0.0.0.0:3000->3000/tcp` |
| HTTP `GET /` | **200**, `<title>Gitness</title>` |
| Contract `ADMIN_PASSWORD` | generated; embedded value baked into `GITNESS_PRINCIPAL_ADMIN_PASSWORD` (non-contract key) as designed |
