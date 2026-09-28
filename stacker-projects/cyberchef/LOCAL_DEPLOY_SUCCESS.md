# cyberchef — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fix applied (with user confirmation)

Removed the empty `config_contract.services.app.fields: {}` block — the parser
refuses service blocks that declare nothing (same class as audiobookshelf). CyberChef
is stateless (no env, no volumes, no secrets) so no policy is needed; see `BUGS.md`.

## Commands

```bash
cd stacker-projects/cyberchef
set -a; source ../../.env; set +a
stacker config validate     # ✓ valid (after fix)
stacker deploy --target local
```

## Verification

| Check | Result |
|---|---|
| Container | `cyberchef-app-1` Up, `0.0.0.0:8000->8080/tcp` |
| HTTP `GET /` | **200**, CyberChef UI HTML (`<title>CyberChef</title>`) |
| Logs | clean |

## Notes

- Port mapping `"8000:8080"` is correct for `ghcr.io/gchq/cyberchef` (listens on 8080).
- Single container, no secrets — no generator work needed.
