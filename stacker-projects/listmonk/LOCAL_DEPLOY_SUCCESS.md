# listmonk — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (app.command class): `command: sh -c "yes | ./listmonk --install; exec ./listmonk"` —
listmonk requires a one-time `--install` (schema + admin) which **prompts
`continue (y/N)?`** and dies on EOF. `yes |` answers it; subsequent boots re-run
install (harmless wipe of empty tables) then serve.

## Verification

| Check | Result |
|---|---|
| Containers | `listmonk-app-1` Up, `listmonk-postgres-1` (healthy) |
| HTTP `GET /` (9000) | **200** |
