# floci — Cloud Deploy Success

**Date:** 2026-11-02
**Stacker:** 0.3.4 (6123cee), target: fresh Hetzner cloud (cpx22, nbg1)
**Server:** floci-1025 (id=947) @ 2.31.185.50
**Template:** stacker.yml (app `floci/floci:nightly` :4566 + `floci/floci-ui:0.7.0` :4500)
**Deployment:** #1526 (hash `deployment_fb1e2143-afae-4089-9888-d5f4635289a4`)

## Commands

```bash
cd stacker-projects/floci
./scripts/generate-secrets.sh
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
stacker deploy --target cloud --key htz-13 --force-new          # #1524/#1525 (paused — backend redis regression, see BUGS.md)
stacker deploy --target cloud --key htz-13 --server floci-1025  # #1526 — completed after the redis fix
```

Note: cloud credentials are **project-scoped** — floci resolves `htz-13`.
Deployments #1524/#1525 ended `paused [internal_error]` on the Stacker
backend redis regression (`ServerInfo.get_from_cache()` got `None` →
"Could not get IP from redis"); after the maintainer's redis fix the
server-reuse redeploy (#1526) completed cleanly.

## Verification (deployment #1526)

| Check | Result |
|---|---|
| `stacker status` | ✓ #1526 — completed |
| `✓ Your SSH key authorized (~/.ssh/id_rsa.pub)` | present |
| `stacker agent status --deployment <hash>` (pinned, stacker#234) | ● online; `project-app-1` + `project-floci-ui-1` running |
| `curl http://2.31.185.50:4566/_floci/health` | **200** — JSON `{"version":"nightly-11012026","services":{"ssm":"running","sqs":"running","s3":"running","dynamodb":"running",...}}` |
| `curl http://2.31.185.50:4500/` | **200** — Floci UI |

## Notes / caveats (see BUGS.md)

- `project-app-1` reports `(unhealthy)` — false negative from the template's
  curl-based healthcheck (curl absent from the image); the API serves 200
  and the deployment completed regardless. The image ships its own
  `healthcheck.sh` for a future fix.
- UI→API wiring (`FLOCI_ENDPOINT: http://floci:4566`) and
  `FLOCI_SERVICES_DOCKER_NETWORK: floci_default` remain broken per BUGS.md —
  the pages load but the UI cannot reach the API and spawned service
  containers cannot attach to the (nonexistent) network.
- Auto-firewall opened **4500** publicly despite `public_ports: ['4566']`
  (over-broad behavior, same class as the bunkerweb 6379 finding) — both
  ports are externally reachable.
- Server left running (servers are never deleted).
