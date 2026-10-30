# strata — known issues

## [BLOCKED] Local deploy: x86-64 + NVIDIA GPU stack cannot build/run on this host

**Date:** 2026-10-30
**CLI:** stacker 0.3.4 (6123cee)
**Host:** arm64 macOS (Apple Silicon), Docker Desktop 4.95 (12 vCPU / 8 GB VM)

Steps to reproduce:
1. `cd stacker-projects/strata`
2. `stacker deploy --target local` (compose built via
   `deploy.compose_file: docker-compose.yml` → `up -d --build`)

Expected behaviour:
Image builds and the app starts (the fixture defaults `deploy.target: local`).

Actual behaviour:
**Build fails** — the engine is x86-64-only (AVX intrinsics), and the CUDA
base image `nvidia/cuda:13.0.0-devel-ubuntu24.04` resolves to its **arm64
(SBSA)** variant on this host:

```
#15 17.07 FAILED: [code=1] CMakeFiles/strata_core.dir/src/core/graph.cpp.o
#15 17.07 /usr/bin/c++ ... -isystem /usr/local/cuda/targets/sbsa-linux/include ...
#15 17.07 /opt/strata/src/core/graph.cpp:4:10: fatal error: immintrin.h: No such file or directory
#15 17.07     4 | #include <immintrin.h>
#15 17.07 compilation terminated.
...
#15 20.62 ninja: build stopped: subcommand failed.
```

`setup.py` auto-retried once ("the build stopped - trying it once more") and
failed identically. Stacker surfaced it as:

```
✗ Deployment to local failed: docker compose failed: Image strata:local Building
```

Even on an x86-64 host the run is hardware-gated: the compose sets
`gpus: all`, and this host has no NVIDIA runtime (probed directly):

```
$ docker run --rm --gpus all alpine:3 true
docker: Error response from daemon: failed to discover GPU vendor from CDI: no known GPU vendor found
```

The fixture's own `.env.example` states the requirements: "NVIDIA GPU 12 GB+
VRAM (driver 580+, nvidia-container-toolkit), 32 GB+ RAM, ~80 GB free disk,
x86-64 with AVX2", and the first start downloads ~70 GB of model.

Logs / Evidence:
- `/tmp/strata-local-deploy.log` (full stacker run: hook → `docker compose
  -p strata --env-file .env --file docker-compose.yml up -d --build`).
- Stacker-side pipeline behaved correctly throughout: `stacker config
  validate` (only W004 below), `--dry-run` OK, pre_build hook
  (`./scripts/pre-build.sh` → generate-secrets + git clone) ran under the
  cleared hook environment, custom `deploy.compose_file` was honoured.

Scope note: the fixture is local-only by design (`deploy:` has no `cloud:`
or `server:` sections → E001/E002 on remote targets), and no Hetzner CPU
server could run it anyway (NVIDIA GPU requirement), so the cloud and
existing-server phases are N/A for this project.

## [BUG] W004: marketplace.long_description missing

**Date:** 2026-10-30

Steps to reproduce:
1. `cd stacker-projects/strata`
2. `stacker config validate`

Expected behaviour:
`✓ Configuration is valid`.

Actual behaviour:
```
Configuration issues:
  - [W004] warning (marketplace.long_description): long_description is missing (100-5000 characters required)
```
`stacker.yml` has a `marketplace:` block (display_name + short_description)
but no `long_description` — the publish gate requires 100–5000 chars. Same
fixture class as the "marketplace: add missing long_description" fixes in
commit `410516fe` (12 other templates). Fixing needs a `stacker.yml` edit
(fixture change — pending user approval).

## [BUG] Deploy summary claims "no local Dockerfile build" while compose_file builds

**Date:** 2026-10-30
**Severity:** Low (UX/reporting only)

Steps to reproduce:
1. `cd stacker-projects/strata`
2. `stacker deploy --target local --dry-run` (and the real run)

Expected behaviour:
Preview reflects what will actually run. The project builds `strata:local`
from `strata-src/Dockerfile` via its `deploy.compose_file`
(`docker-compose.yml` has `build: context: ./strata-src`).

Actual behaviour:
Preview prints `App image source: image=trydirect/strata:0.1.44 (no local
Dockerfile build)` — analysing only `app.image` — but the real deploy runs
`docker compose ... up -d --build`, which builds the local Dockerfile. The
app section's `image:` is ignored when `deploy.compose_file` is set
(comments in the compose file reference deploy.rs:3857). Misleading when
sizing/estimating a deploy; also note `stacker.yml`'s `app:` carries both
`image:` and `dockerfile:` (documented as mutually exclusive) — validate
does not flag it.
