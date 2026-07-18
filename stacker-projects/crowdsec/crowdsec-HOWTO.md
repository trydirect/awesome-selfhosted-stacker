# CrowdSec — Stacker Deploy HOWTO

Single container: `crowdsecurity/crowdsec:latest`. Collaborative threat detection and blocking.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Notes

- No exposed ports (runs as background security agent)
- Data: `crowdsec_config` (rules), `crowdsec_data` (decisions, alerts)
- Reads host logs at `/var/log`
- Community-driven threat intelligence
- Integrates with nginx, Traefik, Cloudflare
