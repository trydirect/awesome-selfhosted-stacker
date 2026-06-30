# Coolify on TryDirect with Stacker

Product vendors can add `stacker.yml` to their repo so users can install,
manage, and monitor the app with TryDirect Stacker.

This Coolify example deploys to Hetzner Cloud. Users only need Stacker, a
Hetzner token, and an SSH key.

## Why TryDirect and Stacker

- Simple for users: one repo, one `stacker.yml`, one deploy command.
- Good for vendors: ship a tested install path without writing custom
  installers for every cloud.
- Built with Rust: fast CLI, single binary, predictable behavior.
- Uses OpenTofu: cloud infrastructure is provisioned as code.
- Includes operations: status, monitoring, firewall, SSH, and redeploy flows.


## 1. Install Stacker

```bash
curl -fsSL https://raw.githubusercontent.com/trydirect/stacker/main/install.sh | bash
```

## 2. Set up the project

Create the Stacker cloud settings:

```bash
cat > .env <<'EOF'
HETZNER_REGION=fsn1
HETZNER_SERVER_TYPE=cpx22
EOF

export HCLOUD_TOKEN='<your-hetzner-cloud-token>'
stacker config show
```

Coolify app settings and secrets are in `docker/production/.env`.

## 3. Deploy

Preview, deploy, then watch status:

```bash
stacker deploy --env production
```

Check the remote containers through the Stacker agent:

```bash
stacker list deployments --limit 1
stacker agent status --deployment <deployment-hash>
```

## 4. Configure the firewall

Most users should open the cloud provider firewall first. For Hetzner Cloud,
list servers, copy the server ID, then open HTTP and HTTPS:

```bash
stacker list servers
stacker cloud firewall add \
  --server-id <server-id> \
  --public-ports 80/tcp,443/tcp
stacker cloud firewall list --server-id <server-id>
```

If you also need guest OS firewall rules, use the agent iptables command:

```bash
stacker list deployments --limit 1
stacker agent configure-firewall \
  --action add \
  --public-ports 80/tcp,443/tcp \
  --persist \
  --deployment <deployment-hash>
```

List the current iptables rules:

```bash
stacker agent configure-firewall --action list --deployment <deployment-hash>
```

## 5. Change a secret and redeploy

Update an existing secret:

```bash
sed -i.bak 's/^DB_PASSWORD=.*/DB_PASSWORD=replace-me/' docker/production/.env
rm docker/production/.env.bak
stacker deploy --env production
```

Add a new secret:

```bash
printf '\nMY_NEW_SECRET=replace-me\n' >> docker/production/.env
stacker deploy --env production
```

## 6. Connect with SSH if needed

After deploy, Stacker stores the server IP locally:

```bash
SERVER_IP=$(sed -n 's/^server_ip: //p' .stacker/deployment-cloud.lock)
ssh -i ~/.ssh/id_ed25519 root@"$SERVER_IP"
```

If Stacker SSH access breaks, inject the Stacker-managed key again:

```bash
stacker ssh-key inject --server-id <server-id> --with-key ~/.ssh/id_ed25519
```
