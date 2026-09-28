# homer — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. Empty `config_contract` block → volume policy (`homer_config: generated`).
2. `cp config.yml .stacker/` staged before deploy — `./config.yml` bind resolves
   against `.stacker/` locally (root `BUGS.md` entry).

## Verification

| Check | Result |
|---|---|
| Containers | `homer-app-1` Up (healthy), `homer-caddy-1` |
| HTTP `GET /` | **200**, `<title>Homer</title>` |
