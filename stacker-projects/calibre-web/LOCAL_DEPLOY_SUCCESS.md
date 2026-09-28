# calibre-web — Local Deploy Success

**Date:** 2026-09-26
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture changes needed for this one.

## Commands

```bash
cd stacker-projects/calibre-web
set -a; source ../../.env; set +a
stacker config validate            # ✓ valid
stacker deploy --target local
```

## Verification

| Check | Result |
|---|---|
| `stacker config validate` | ✓ valid |
| Container | `calibre-web-app-1` Up, `0.0.0.0:8083->8083/tcp` |
| HTTP `GET /` | 302 → `/login?next=%2Fadmin%2Fdbconfig` → **200** (first-run wizard) |
| Logs | clean — `ls.io-init done`, kepubify paths set, listening on 8083 |
| Volumes | `calibre-web_calibre_config`, `calibre-web_calibre_library` created |

## Notes

- `linuxserver/calibre-web:latest` is multi-arch — no `DOCKER_DEFAULT_PLATFORM`
  workaround needed (unlike automatisch/calcom).
- `config_contract` carries the same junk `volumes: {mutability: editable}` field
  seen on automatisch (misnested volumes block → fake env field). Cosmetic; logged
  in the project notes of this file. `PGID`/`PUID`/`TZ` editable declarations are fine.
- Port 8083 free — no conflicts.
