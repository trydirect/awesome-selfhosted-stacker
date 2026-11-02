# waha — Cloud Deploy Success

**Date:** 2026-11-02
**Stacker:** 0.3.4 (6123cee), target: fresh Hetzner cloud (cpx22, fsn1)
**Server:** waha-254d (id=353) @ 2.31.175.24
**Template:** stacker.yml (image `devlikeapro/waha:latest-2026.9.2`, port 3000)
**Deployments:** #557 provisioned the server (SSH-key install failed — see
below); #558 (hash `deployment_c0e1249f-f899-4769-82cf-dc37cb5971ca`)
completed the fix and is the verified deployment.

## Template fixes applied (user-approved "fix waha")

- `config_contract.services.app.fields.WHATSAPP_API_KEY_EXCLUDE_PATH`:
  `mutability: provided` → `editable`. It is not a secret; `provided` would
  **blank** the author default (`ping,health`) on marketplace installs, after
  which the `curl localhost:3000/health` healthcheck would get 401 and the
  container would never go healthy.
- `config_contract`: removed the healthcheck-internal pseudo-fields
  (`healthcheck`, `interval`, `retries`, `start_period`, `test`, `timeout`,
  `volumes`) — same defect class as the bunkerweb cleanup.

## Commands

```bash
cd stacker-projects/waha
./scripts/generate-secrets.sh        # fills WAHA_API_KEY only
# BASE_PATH/DEPLOY_HOST were empty in .env — filled (see BUGS.md):
#   BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
#   DEPLOY_HOST=2.31.175.24          (waha's own server)
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples

stacker deploy --target cloud --key htz-5 --force-new          # #557 (new VPS)
stacker deploy --target cloud --key htz-5 --server waha-254d   # #558 (SSH fix)
```

Note: cloud credentials are **project-scoped** — waha's project resolves
`htz-5` (id=5), not the `htz-0` used by other projects.

## Verification (deployment #558)

| Check | Result |
|---|---|
| `✓ Your SSH key authorized (...stacker-project-test.pub)` | present (absent on #557 — BASE_PATH bug) |
| `stacker agent status --deployment <hash>` (pinned, stacker#234) | ● online; `project-app-1` running |
| `docker inspect project-app-1` | `health=healthy` ("Up (healthy)") |
| `curl http://2.31.175.24:3000/ping` | **200** (`pong`) |
| `curl http://2.31.175.24:3000/health` | **200** |
| `curl /api/sessions` without key | **401** (auth enforced) |
| `curl /api/sessions` with `X-Api-Key` (generated `WAHA_API_KEY`) | **200** (session list) |

Both auth-excluded paths (`ping,health` per `WHATSAPP_API_KEY_EXCLUDE_PATH`)
work without a key, and the API key gate works — the generated secret is
functional end to end.

Notes:
- WhatsApp itself needs a phone to pair (QR via `/api/sessions`) — out of
  scope for deploy verification; the gateway API is fully exercised above.
- Local (arm64) remains blocked: upstream publishes single-arch tags only
  (`latest*` amd64, `arm*` arm64 — no multi-arch manifests), see BUGS.md.
- Server left running (servers are never deleted).
