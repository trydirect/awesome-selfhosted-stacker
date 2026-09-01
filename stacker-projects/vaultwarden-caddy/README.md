# vaultwarden proxy/secrets test variants

Four projects derived from a single **vaultwarden** base
(`vaultwarden/server:latest`, single container, web UI on container port 80),
each exercising a different Stacker feature:

| Project | Feature under test | `proxy.type` |
|---------|--------------------|--------------|
| `vaultwarden-traefik` | reverse proxy — Traefik (label-based routing) | `traefik` |
| `vaultwarden-npm`     | reverse proxy — Nginx Proxy Manager (admin-API routing) | `nginx-proxy-manager` |
| `vaultwarden-caddy`   | reverse proxy — Caddy (Caddyfile routing) | `caddy` |
| `vaultwarden-secrets` | secret management via `stacker secrets` | `none` |

All four share the same app + `ADMIN_TOKEN` secret; the proxy variants add a
`proxy:` block routing `vault.example.com → app:80`.

## Commands used

### 1. Manage secrets (local `.env` mode)
`stacker secrets` writes a `0600` project `.env`; `list`/`get` mask values by
default; `validate` checks every `${VAR}` in `stacker.yml` is set.

```bash
cd stacker-projects/vaultwarden-caddy          # (repeat per variant)

# Set the app secret + deploy-time vars into .env (never committed)
stacker secrets set ADMIN_TOKEN="$(openssl rand -base64 48 | tr -d '\n=+/' | head -c 40)"
stacker secrets set DEPLOY_HOST="46.224.127.228"
stacker secrets set BASE_PATH="/absolute/path/to/stacker-project-examples"

stacker secrets list          # WIKIJS_DATABASE_PASSWORD=***  (use --show to reveal)
stacker secrets get ADMIN_TOKEN
stacker secrets validate      # ✓ All N variable(s) are set
```

### 2. Validate the config
```bash
stacker config validate       # ✓ Configuration is valid
```

### 3. Deploy to a fresh cloud server
```bash
set -a; source .env; set +a           # export DEPLOY_HOST / BASE_PATH for ${VAR} resolution
stacker deploy --target cloud --force-new
```
- `--force-new` provisions a brand-new Hetzner server instead of reusing
  `deploy.server` (needed here because `deploy.target: server` points at an
  existing host for the non-cloud path).
- Regenerate the `.stacker/` bundle after editing `stacker.yml` by removing it
  first (`rm -rf .stacker`) or passing `--force-rebuild`.

### 4. Watch / inspect
```bash
stacker status                        # deployment state, IP, emergency SSH
stacker deployment events             # full role-level event log (incl. tofu errors)
```

## How each proxy variant routes
- **traefik** — the CLI generates Traefik routing **labels** on the app
  container; the platform Traefik role reads them. No config file.
- **caddy** — the platform Caddy role renders `/home/trydirect/caddy/Caddyfile`
  from the deploy's `proxy.domains`. For `--target local`, the CLI renders
  `.stacker/Caddyfile` itself.
- **nginx-proxy-manager** — NPM has no config file; the platform role creates a
  **proxy host** via NPM's admin API from `proxy.domains`.

In every case the proxy is **platform-managed**: the CLI strips it from the
remote compose (`Excluding platform-managed service(s)… <proxy>`) and its own
Ansible role deploys it, so it is not double-deployed inside the project compose.

## Verification
```bash
# Through the proxy (Host header selects the site):
curl -H "Host: vault.example.com" http://<server-ip>:80/
# Direct (secrets variant / debugging), vaultwarden is also published on 8080:
curl http://<server-ip>:8080/
```
Expect the Vaultwarden web vault to load (HTTP 200).
