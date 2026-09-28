# lemmy — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix: **added `config.hjson`** (`hostname: "lemmy.example.com"`) + bind mount
`./config.hjson:/config/config.hjson:ro`. Lemmy panics without a settings file
(`Failed to load settings file`) and `{}` alone is insufficient (`Hostname variable
is not set!` — `hostname` must be in the file). Staged into `.stacker/` for the
local bind (root `BUGS.md` class).

## Verification

| Check | Result |
|---|---|
| Containers | `lemmy-app-1` Up, `lemmy-lemmy-db-1` (healthy), `lemmy-lemmy_pictrs-1` |
| HTTP `GET /` (8536) | **200** |
