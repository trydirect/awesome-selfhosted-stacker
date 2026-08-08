# Template Revision — Add NPM + Auto-SSL to Every Stack

## Problem

Current templates (see `stacker-projects/dify/stacker.yml` for reference) ship with:

```yaml
proxy:
  type: none
  domains: []
```

This means every user who deploys the stack has to set up their own reverse proxy and SSL certificate after the fact. That kills the "10-minute production-ready" pitch — the last 3 hours are the operator wiring nginx by hand.

## Fix — one-line pattern per template

Change the `proxy:` block in every `stacker.yml` to:

```yaml
proxy:
  type: nginx-proxy-manager
  auto_detect: true
  domains:
    - domain: "${commonDomain}"
      ssl: auto
      upstream: "<container-name>:<internal-port>"
```

Where:

- `${commonDomain}` is pulled from `install.inputs.commonDomain` (already present in every template — just needs to be referenced from the proxy block)
- `<container-name>` is the container that serves the app's landing UI on the docker network
- `<internal-port>` is the container-side port (not the host bind)

## Per-stack mapping (three AI stacks first)

| Stack | Landing container | Internal port | Suggested demo subdomain |
|---|---|---|---|
| `ai-knowledge-base` | dify web (check the compose — usually `dify-web` or `dify-nginx`) | 80 | `ai-knowledge-base.try.direct` |
| `private-sovereign-ai` | `open-webui` | 8080 | `private-sovereign-ai.try.direct` |
| `ai-automation-workflows` | `flowise` (primary) + `n8n` (secondary) | 3000 / 5678 | `ai-automation-workflows.try.direct` + `n8n.<...>.try.direct` |

For stacks that expose multiple UIs (like ai-automation-workflows), declare multiple `domains:` entries in one proxy block:

```yaml
proxy:
  type: nginx-proxy-manager
  auto_detect: true
  domains:
    - domain: "${commonDomain}"
      ssl: auto
      upstream: "flowise:3000"
    - domain: "n8n.${commonDomain}"
      ssl: auto
      upstream: "n8n:5678"
    - domain: "qdrant.${commonDomain}"
      ssl: auto
      upstream: "qdrant:6333"
```

## Rollout plan

1. **Start with the 3 AI stacks** (they're the tip of the spear for the AI-agency positioning). Get one working end-to-end, then replicate the pattern.
2. **Verify the pattern on the live demo servers** (62.238.110.174, 62.238.38.158, 65.109.165.211). If deploy works cleanly, the pattern is safe.
3. **Roll pattern into remaining 67+ templates**. Can be batched — do 10 at a time, PR each batch.
4. **Update each template's README** with the new "just set commonDomain and stacker deploy" flow (delete any manual nginx/SSL setup sections).

## Verification per template

After editing:

```bash
cd stacker-projects/<name>
stacker config validate
stacker deploy --dry-run
```

Then, on the demo server:

```bash
stacker deploy
# wait 30s for NPM to request cert
curl -I https://<subdomain>.try.direct
# expect: HTTP/2 200, valid SSL
```

## Gotchas

- **DNS must exist before deploy** or Let's Encrypt HTTP-01 fails. Add A record → wait 2 min → deploy.
- **NPM must expose 80 and 443 publicly**. If the cloud firewall isn't open, cert issuance fails silently. Ensure `deploy.cloud.public_ports: ["80", "443"]` in stacker.yml for cloud targets.
- **Container name must match what NPM sees on the docker network**. Some compose files rename services vs. containers — always use the container name (or the service alias) that's actually joined to the shared network.
- **Websockets** — Flowise, n8n, Open WebUI all need websockets. NPM proxies them by default, but confirm on the first deploy.

## After this lands

The `/oss` landing page's claim "🟢 See it live" links will resolve to real HTTPS subdomains that the operator (or a demo prospect) can click. That turns the page from a marketing claim into working proof.

The pillar-1 TikTok scripts also get an upgrade: instead of showing `stacker deploy` → some `localhost:3001` port, the demo ends at a clean `https://ai-knowledge-base.your-domain.com` — significantly higher perceived polish.
