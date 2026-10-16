# langchain-chatchat — known issues

## [BUG] xinference image was GPU-built — `libcuda.so.1` crash-loop on CPU hosts

**Severity:** High (service unusable on any CPU-only host)
**Date:** 2026-10-16
**Status:** FIXED 2026-10-16 — pinned `xprobe/xinference:v0.12.3-cpu`

### Summary
`xprobe/xinference:v0.12.3` imports `llama_cpp` → loads `libllama.so` →
requires `libcuda.so.1` at startup and crash-loops on hosts without NVIDIA:

```
RuntimeError: Failed to load shared library '.../libllama.so':
libcuda.so.1: cannot open shared object file: No such file or directory
```

### Fix
```yaml
  - name: xinference
    image: xprobe/xinference:v0.12.3-cpu   # same version, CPU variant
```
Verified on a CPU cpx42: `project-xinference-1 Up (healthy)`,
`curl localhost:9997/status` → worker JSON, and chatchat → xinference
network call returns 200.

## [NOTE] Earlier resource-floor note is superseded

The previous "not deployable — 14 GB image" note applied to the 2 GB shared
test server. On cpx42 (16 GB RAM / 300 GB disk) the stack deploys and runs
fine (see EXISTING_DEPLOY_SUCCESS.md). The 2024-era images work.
