# n8n

**Self-hosted workflow automation** - a Zapier alternative with a visual
editor, on a server you already have.

## Deploy to your own server

```bash
brew install trydirect/tap/stacker        # or the installer below
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/n8n

cp .env.example .env
# set DEPLOY_HOST, DEPLOY_USER, SSH_KEY_PATH and ADMIN_EMAIL in .env
./scripts/generate-secrets.sh             # fills the passwords and the key

stacker deploy
```

No TryDirect account is needed for any of this. All we ask of the server is
SSH access with a key you already have.

Without Homebrew:

```bash
curl -fsSL https://raw.githubusercontent.com/trydirect/stacker/main/install.sh | bash
```

## What you get

| Service | Port | Image |
|---------|------|-------|
| n8n | 5678 | `n8nio/n8n:2.45.4` |
| PostgreSQL | internal | `postgres:17.11-alpine` |

The instance owner is created on first start from `ADMIN_EMAIL` and the
generated `ADMIN_PASSWORD`, so nobody who finds the port first can claim the
instance. `N8N_ENCRYPTION_KEY` is generated per deployment and encrypts the
credentials n8n stores for the services you connect it to.

## Read this before you store credentials in it

This stack serves n8n over **plain HTTP on port 5678**, and sets
`N8N_SECURE_COOKIE=false` to make that work. That is fine for trying it out on
a machine you control. It is not fine once n8n holds API keys for your other
services, which is the whole point of n8n - anyone who can see the traffic
sees the session cookie.

Put it behind TLS before real use: a reverse proxy on the same box, or your
existing one. 68 of the projects in this repository use the `caddy` proxy type
for exactly this, and `stacker.yml` here is one block away from the same.

## Deploy to a new cloud server instead

```bash
stacker deploy --target cloud
```

Provisions a Hetzner cpx22 in fsn1 with your own provider key, opens port
5678, and deploys the same stack. The server appears in your cloud account,
not ours.
