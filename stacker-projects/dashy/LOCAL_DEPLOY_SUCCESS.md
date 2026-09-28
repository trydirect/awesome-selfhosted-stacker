# dashy — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fix applied (pre-approved fix class)

Empty `config_contract.services.app.fields: {}` replaced with a real volume policy
(dashy has no env vars but one volume):

```yaml
config_contract:
  services:
    app:
      volumes:
        dashy_config: { mutability: generated }
```

## Commands

```bash
cd stacker-projects/dashy
set -a; source ../../.env; set +a
stacker config validate      # ✓ valid
stacker deploy --target local
```

## Verification

| Check | Result |
|---|---|
| Container | `dashy-app-1` Up (healthy), `0.0.0.0:8082->8080/tcp` |
| HTTP `GET /` | **200** |
| Logs | clean (update check completes) |

## Server test: BLOCKED (environment)

See project `BUGS.md` / root `BUGS.md`: host port 8082 is owned by the box's
GitLab deployment; the remote container failed to bind and **stacker reported the
deploy as successful anyway** (silent failure — root `BUGS.md` entry).
Result recorded as: local pass, existing-server blocked (not a template defect).
