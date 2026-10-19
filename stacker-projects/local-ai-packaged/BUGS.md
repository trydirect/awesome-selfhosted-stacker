# local-ai-packaged — known issues

## [BUG] `ollama-gpu-amd` devices `/dev/kfd` abort the whole compose up on CPU hosts

**Severity:** High (deploy impossible on any CPU-only host — cloud and server)
**Date:** 2026-10-19
**Status:** documented only (fix options listed below; not applied by user
choice — needs `profiles` support in stacker or an agreed template change)

### Steps
1. `stacker deploy --target server --server-host <cpu-host>` (deployment
   #1385) — or `--target cloud --force-new` (#1382, #1383).

### Actual
Ansible's `docker compose up -d --remove-orphans` fails with rc=1:
```
Error response from daemon: error gathering device information while adding
custom device "/dev/kfd": no such file or directory
```
- The AMD-ROCm variant service `ollama-gpu-amd` declares
  `devices: [/dev/kfd, /dev/dri]`; CPU hosts have no `/dev/kfd`, and a single
  failing service **aborts the entire compose up** (many containers stay
  `Created`, some `Restarting`).
- On the cloud path (#1382/#1383) this presented as
  `paused [local_exec_provisioner_error]` ("host port already in use" is only
  the generic hint) plus a secondary SSH-authorize API timeout; on the server
  path (#1385) as `paused [internal_error]` with the exact docker error above.
- The same `devices` declaration is why a local deploy on Apple Silicon
  fails (amd64-only rocm image + device passthrough).

### Root cause class
Upstream compose gates these variants behind `profiles: [gpu-nvidia]` /
`[gpu-amd]`; **stacker.yml's `services[]` schema has no `profiles` field**, so
GPU variants are always generated and always started.

### Fix options (not applied)
1. Replace `devices` with `privileged: true` on `ollama-gpu-amd` — works on
   AMD-GPU hosts (privileged gets all devices) and does not fail on CPU hosts.
2. Drop the `ollama-gpu-amd` service from `scripts/build-services.py` (AMD
   support lost).
3. Add `profiles` support to stacker core (the proper fix; belongs with the
   planned core PR) and gate both GPU variants.

Remember: `services:`/`volumes:`/`config_contract` are generated — edit
`scripts/build-services.py` and regenerate, not the generated block.

### Evidence
- Deployment #1385 Ansible task: `docker compose -f
  /home/trydirect/project/docker-compose.yml up -d --remove-orphans` → rc 1,
  stderr ends with the `/dev/kfd` error; PLAY RECAP `failed=1`.
- Deployments #1382/#1383 (cloud, servers 861/862): identical
  `local_exec_provisioner_error`, hosts unreachable afterwards.
