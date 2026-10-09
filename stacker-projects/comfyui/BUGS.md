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
