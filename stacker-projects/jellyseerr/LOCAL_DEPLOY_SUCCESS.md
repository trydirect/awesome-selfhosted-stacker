# jellyseerr — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix: empty `config_contract` block → volume policy (`jellyseerr_config: generated`).

## Verification

| Check | Result |
|---|---|
| Container | `jellyseerr-app-1` Up |
| HTTP `GET /` | 302 → `/setup` → **200** (first-run wizard) |
