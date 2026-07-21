# Deploy Ghost with `stacker install`

*One command to configure, one command to deploy.*

---

## Prerequisites

- Stacker CLI installed (`cargo install stacker-cli` or `curl -fsSL https://stacker.try.direct/install.sh | bash`)
- Authenticated: `stacker login`
- A Hetzner cloud credential saved (verify with `stacker list clouds`)

---

## Install

```bash
stacker install ghost \
  --domain blog.example.com \
  --key htz-0 \
  --provider hetzner \
  --region fsn1 \
  --size cx23
```

This writes a `stacker.yml` with Ghost and MySQL pre-configured.

| Flag | Required | Example | Notes |
|------|----------|---------|-------|
| `--domain` | no | `blog.example.com` | Sets the blog URL |
| `--key` | yes (cloud) | `htz-0` | Saved credential from `stacker list clouds` |
| `--provider` | yes (cloud) | `hetzner` | `hetzner`, `digitalocean`, `aws`, `linode`, `vultr` |
| `--region` | yes (cloud) | `fsn1` | `fsn1`, `nbg1`, `hel1` (Hetzner) |
| `--size` | yes (cloud) | `cx23` | `cx23` (2 vCPU, 4 GB), `cx33` (2 vCPU, 8 GB) |
| `--set` | no | `key=value` | Override any install input, repeatable |
| `--name` | no | `my-ghost` | Project name override |
| `--file` | no | `./ghost.yml` | Custom output path |

---

## Deploy

```bash
stacker deploy --target cloud --key htz-0 --force-new
```

Stacker provisions the server, installs Docker, transfers the compose file, and starts the containers. The output includes the server IP:

```
Server details: ghost-ae91 (root@94.130.99.220:22)
```

### Deploy to an existing server

```bash
stacker deploy --target server
```

Requires `deploy.server.host` in `stacker.yml`.

### Redeploy with changes

```bash
stacker deploy --target cloud --key htz-0 --force-rebuild
```

---

## Verify

```bash
stacker status
```

Shows running containers, ports, and health. Then open `http://<SERVER_IP>:2368` in your browser to complete setup.

---

## Open Ports

By default only SSH (22) is open. Open Ghost's port:

```bash
stacker cloud firewall add --public-ports 2368/tcp
```

---

## Status & Logs

```bash
stacker list deployments
stacker deployment events --deployment <HASH>
stacker agent logs ghost
```

---

## Other Templates

```bash
# List all
stacker templates --json

# Search
stacker find wordpress --json

# Install any template
stacker install <slug> --domain <domain> --key <credential> --provider <provider> --region <region> --size <size>
```

---

## Clean Up

```bash
stacker destroy
```

---

## Caveats

- **`--key` must match a saved credential name** from `stacker list clouds`. Typos result in "Cloud API credentials are required."
- **`--domain` sets the install input** but doesn't configure DNS or a reverse proxy. You'll need to set that up separately.
- **Port 2368 is closed by default** on cloud deploys. Use `stacker cloud firewall add` to open it.
- **Some templates auto-deploy** (ghost, wordpress). Others only write `stacker.yml` and require a separate `stacker deploy`.
- **Marketplace marker** (`# @stacker-origin: marketplace`) in `stacker.yml` blocks hooks. Remove it before deploying if you have custom `pre_build`/`post_deploy` scripts.

---

*Tested with stacker-cli v0.3.1. Ghost 5-alpine + MySQL 8 on Hetzner Cloud.*
