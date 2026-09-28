# gotify — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (pre-approved class): empty `config_contract.services.app.fields: {}`
→ real volume policy (`gotify_data: { mutability: generated }`) — same as dashy.

## Verification

| Check | Result |
|---|---|
| Container | `gotify-app-1` Up (healthy), `0.0.0.0:8080->80/tcp` |
| HTTP `GET /` | **200**, `<title>Gotify</title>` |
