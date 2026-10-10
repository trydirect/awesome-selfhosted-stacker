# ComfyUI — Stacker Deploy

Self-hosted ComfyUI node for AI image/video generation workflows.

## Minimal server requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| vCPU | 4 | 8 (cpx42) |
| RAM | 8 GB | 16 GB |
| Disk | 100 GB free | 200 GB |
| GPU | none (CPU inference) | not required |

The `ashleykza/comfyui` image ships a full nvidia/cudnn stack; it unpacks to
**~25 GB** on disk even without a GPU. This is why a 40 GB test server fails
with `no space left on device`. The template defaults to a **cpx42**
(8 vCPU / 16 GB / 320 GB) for cloud deploys.

Actual generation runs on CPU here and is slow — this stack is for testing
workflows, not production inference. Loading a ~7 GB SDXL model needs ~16 GB
RAM headroom.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker deploy --target cloud --force-new          # fresh cpx42 server
# or: stacker deploy --target server --server-host <ip> --server-user root
```

UI listens on port `8188` (public_ports opened in stacker.yml).

## Environment

- `PRELOAD_MODELS` — JSON array of model names to preload at start, default `[]`
- `CLI_ARGS` — extra args appended to the comfy launcher
