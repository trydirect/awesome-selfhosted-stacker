# woodpecker-ci — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): image tags `:latest` → `:v3` (upstream removed
`:latest` intentionally, exit 30), `WOODPECKER_GITEA=true` + server URL (v3 refuses
to start with "forge not configured"), contract-key sync `WOODPECKER_AGENT_SECRET`
(generator wrote `AGENT_SECRET` only), added `deploy:` block (was missing → E002).

## Verification

| Check | Result |
|---|---|
| Containers | `app` + `woodpecker-agent` both **healthy** |
| HTTP `GET /` (8000) | **200** |
