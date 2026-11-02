# floci — Local Deploy Success

**Date:** 2026-11-02
**Stacker:** 0.3.4 (6123cee), target: local (`--target local`)
**Template:** stacker.yml (app `floci/floci:nightly` :4566 + `floci/floci-ui:0.7.0` :4500)

## Commands

```bash
cd stacker-projects/floci
./scripts/generate-secrets.sh
stacker deploy --target local
```

## Verification

| Check | Result |
|---|---|
| Containers | `floci-app-1`, `floci-floci-ui-1` Started (network `floci_app-network`) |
| `curl http://localhost:4566/_floci/health` | **200** — JSON: ssm/sqs/s3/dynamodb/sns/lambda/apigateway/iam/kafka/mq/elasticache… all `running` |
| `curl http://localhost:4500/` | **200** — `<title>Floci UI</title>` |
| `stacker` pipeline | clean: config validated (lint-only), both images pulled, containers created/started, "✓ Local deployment started successfully" |

## Caveats (template defects — see BUGS.md)

- `floci-app-1` reports **(unhealthy)** — false negative: the healthcheck runs
  `curl` which is **not in the image** (`/bin/sh: curl: command not found`),
  while `/_floci/health` serves 200 fine.
- UI→API wiring is broken: `FLOCI_ENDPOINT`/`FLOCI_BASE_URL` use hostname
  `floci`, but the generated compose service is `app` (verified:
  `getent hosts floci` → UNRESOLVED, `getent hosts app` → 172.19.0.2).
  The UI shell (200) cannot reach the API.
- `FLOCI_SERVICES_DOCKER_NETWORK: floci_default` does not exist (generated
  network is `floci_app-network`) — spawned service/lambda containers would
  fail to attach.

Deployment mechanics (the stacker CLI under test) worked correctly
end-to-end; the defects above are fixture wiring issues, logged in BUGS.md.
