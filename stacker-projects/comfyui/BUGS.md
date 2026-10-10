# BUGS.md — comfyui

## [BLOCKED] Server deploy fails: image does not fit 38G test disk

**Date:** 2026-10-09
**Deployment:** #1255, #1271, #1275, #1276, #1277 (all `paused [internal_error]`)

### Root cause
`ashleykza/comfyui:latest` includes full nvidia/cudnn stack. Ansible pull+
extract on 46.224.127.228 (38G disk) fails mid-layer:

```
write .../nvidia/cudnn/lib/libcudnn_engines_precompiled.so.9:
no space left on device
```

Even after `docker system prune -af --volumes` + `docker builder prune -af`
(22G free) the image still does not fit.

### Not a stacker bug
Template is deployable on a server with ≥50G free disk. Test server too small.
Marketplace template stays `draft` until a bigger target is available.

### RESOLVED 2026-10-10
Fresh cloud server **cpx42** (8 vCPU / 16 GB / 320 GB, `comfyui-eb3e`,
46.225.158.197) provisioned via `stacker deploy --target cloud --force-new`.
Image fits (27G used / 262G free). Additional fixes needed to boot on CPU:

1. Image's entrypoint reads **`EXTRA_ARGS`**, not `CLI_ARGS` (the env var the
   template originally exposed). `EXTRA_ARGS=--cpu` → CPU inference.
2. Container app listens on **3001** (`start_comfyui.sh` hardcodes
   `--port 3001`), so the compose mapping must be `"8188:3001"`, not
   `"8188:8188"` — otherwise host 8188 forwards to nothing (`connection
   refused` despite "Container is READY!" in logs).

Deployment #1281: HTTP 200 on http://46.225.158.197:8188,
`/system_stats` → comfyui 0.26.0, 16 GB RAM. Submitted to marketplace.
