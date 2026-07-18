# Home Assistant — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/homeassistant:latest`. Home automation platform.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8123/` in a browser.

Create an account on first visit.

## Notes

- Port: 8123
- Data: `ha_config` volume
- Supports 2000+ integrations (Zigbee, Z-Wave, MQTT, etc.)
- Mobile apps available for iOS and Android
