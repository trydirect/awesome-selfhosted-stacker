# waha — known issues

## [BUG] Cannot run locally on Apple Silicon: image has no arm64 manifest

**Severity:** Low for x86_64 servers (template target); blocks local test on arm64
**Date:** 2026-10-16

### Steps
1. `stacker deploy --target local` on macOS/arm64 (image
   `devlikeapro/waha:latest-2026.9.2`).

### Actual
```
Error: ... no matching manifest for linux/arm64/v8 in the manifest list
```
`docker manifest inspect devlikeapro/waha:latest` and
`devlikeapro/waha:latest-2026.9.2` list only `amd64` (+ attestation) — no
arm64 build for any tag checked.

### Expected
Image pulls and container starts (as it will on x86_64 targets).

### Impact / workaround
- Template is deployable to Hetzner/cloud/server (x86_64) — this is a
  local-test limitation only.
- No local verification performed: no container, no health check. `stacker
  destroy`/image cleanup not required (pull failed before container create).

### Fix options
- Upstream arm64 build request, or
- `platform: linux/amd64` (emulation) in the generated compose — slow
  Chromium-based WhatsApp engine under qemu; not applied.

## [BUG] Unresolved `${BASE_PATH}` silently yields a broken SSH key path — deploy "completes" with no SSH access

**Date:** 2026-11-02
**Severity:** High (server provisioned and app deployed, but zero SSH access)

Steps to reproduce:
1. `stacker-projects/waha/.env` has `BASE_PATH=` empty (`generate-secrets.sh`
   only fills `WAHA_API_KEY`).
2. `stacker deploy --target cloud --key htz-5 --force-new` (stacker.yml has
   `deploy.cloud.ssh_key: ${BASE_PATH}/stacker-project-test`).

Expected behaviour:
Fail fast on the unresolved variable before provisioning (or at least before
declaring success).

Actual behaviour:
Deployment #557 reports `✓ Deployment #557 completed`, then errors — after
the server exists and the app is deployed:

```
✗ Your SSH key was not authorized for server 353.
  Reason: deploy.cloud.ssh_key is set but its public key could not be read
  at /stacker-project-test.pub: No such file or directory (os error 2).
  You would have no SSH access with that key.
```

`${BASE_PATH}` resolved to the empty string (`/stacker-project-test.pub`),
and the failure surfaces only at the post-deploy SSH-authorization step. The
app was in fact up (HTTP 200 on /ping and /health) — so the "completed"
status plus a bare error is a misleading mixed signal.

Remedy applied: fill `BASE_PATH` (and `DEPLOY_HOST`) in `.env`, then redeploy
to the *same* server (`--server waha-254d`) — deployment #558 then printed
`✓ Your SSH key authorized`. Suggested CLI improvement: validate
`deploy.*.ssh_key` (and `server.host`) resolution before provisioning, and
fail the deploy status (not just an ancillary check) when key authorization
fails.

## [BUG] Cloud credential lookup is project-scoped but the error doesn't say so

**Date:** 2026-11-02
**Severity:** Low (UX)

Steps to reproduce:
1. From `stacker-projects/bunkerweb`: `stacker cloud keys` shows `htz-0`,
   `htz-13`.
2. From `stacker-projects/waha`: `stacker deploy --target cloud --key htz-0`.

Expected behaviour:
Either the same credential list, or an error that says credentials are
per-project and lists what *this* project can see.

Actual behaviour:
`✗ Configuration validation error: No saved cloud credential found with name
'htz-0'`. `stacker cloud keys` from waha lists a completely different single
credential (`htz-5`) — the store is project-scoped (waha's project is id=406
with `cloud_id: 5`), which nothing in the output explains. Cost one failed
deploy attempt.

## Addendum (2026-11-02) to the arm64 blocker above

Checked Docker Hub (`devlikeapro/waha` tags, per-tag image lists): upstream
publishes **single-arch tags only** — `latest*`, `noweb*`, `chrome*`,
`gows*` are amd64-only; `arm*`, `noweb-arm*`, `gows-arm*` are arm64-only.
No tag has a multi-arch manifest, so no in-template image pin fixes local
Apple Silicon runs; a per-arch image selection or upstream multi-arch
manifests would be needed. `platform: linux/amd64` emulation remains the
only local workaround (slow Chromium engine under qemu; not applied).

## Fixed in this session's template edit (2026-11-02)

- `WHATSAPP_API_KEY_EXCLUDE_PATH` was `mutability: provided` → would be
  blanked on marketplace installs → `/health` healthcheck would 401 and the
  container could never go healthy. Now `editable`.
- Removed healthcheck-internal pseudo-fields from `config_contract`
  (same class as the bunkerweb cleanup).

Stale-context note: `.stacker/deployment-cloud.lock` (#1427, Oct 23) and
`deployment-server.lock` (#1472, Oct 26) predate the current Stacker API
environment — #1427 never got a server, #1472 deployed to the **forbidden
shared host** 46.224.127.228. Neither was reused; the verified deployment
above uses waha's own fresh server 2.31.175.24 per the
fresh-server-per-project rule.
