# WireGuard — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/wireguard:latest`. Modern VPN.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Check container logs for peer QR codes:

```bash
docker logs wireguard
```

## Notes

- Port: 51820/udp
- Data: `wireguard_config` volume
- Requires NET_ADMIN and SYS_MODULE capabilities
- Set `SERVERURL` to your domain or IP in `.env`
- Peer configs generated automatically on first boot
