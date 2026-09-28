# audiobookshelf — Local Deploy Success

**Date:** 2026-09-25
**Target:** local (`--target local`; the file's default `deploy.target: server` was
overridden — the project `.env` still points at the deprecated shared host
46.224.127.228, which per root `.env` notes must not be reused — stacker#240)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fixes applied (with user confirmation)

1. `config_contract.services.app.fields: {}` (empty block) rejected by the parser
   (new "refuse a service block that declares nothing" rule). Replaced with a real
   policy: `TZ: editable` (vendor-documented knob) + volume policy
   (`audiobooks_data/config/metadata: generated` — `/config` holds the
   secret-derived JWT key, so it must not ship in a baked image).
2. Port mapping `"13378:13378"` → `"13378:80"` (container listens on 80; see
   `BUGS.md`).

## Commands

```bash
cd stacker-projects/audiobookshelf
set -a; source ../../.env; set +a
stacker config validate                  # ✓ Configuration is valid
stacker deploy --target local            # first deploy (pre port fix)
stacker deploy --target local --force-rebuild   # after port fix
```

No `generate-secrets.sh` run needed — the template declares no secrets
(`.env.example`: "Audiobookshelf — no secrets needed").

## Verification

| Check | Result |
|---|---|
| `stacker config validate` | ✓ valid |
| Container status | `audiobookshelf-app-1` Up, `0.0.0.0:13378->80/tcp` |
| HTTP `GET http://localhost:13378/` | **200**, audiobookshelf UI HTML |
| Container logs | clean — DB init, `JWT secret key not found, generating one`, `Listening on port :80` |
| Volumes | `audiobookshelf_audiobooks_data`, `_config`, `_metadata` created |
| Network | `audiobookshelf_app-network` created |

## Notes

- Deploy pipeline (pull → network/volumes → compose up) worked end-to-end with no
  stacker-side errors.
- `.stacker/deployment-local.lock` written; `stacker destroy` does not see local
  deployments (root `BUGS.md`) — teardown requires
  `docker compose -p audiobookshelf down -v`.
