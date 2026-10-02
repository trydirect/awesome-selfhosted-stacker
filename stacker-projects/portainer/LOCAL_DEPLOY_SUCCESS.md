# portainer — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (pre-approved): removed empty `config_contract.services.app.fields: {}`.
Docker socket bind mount works locally.

## Verification

| Check | Result |
|---|---|
| Containers | `portainer-app-1` Up |
| HTTP `GET /` (9000) | **200** |
