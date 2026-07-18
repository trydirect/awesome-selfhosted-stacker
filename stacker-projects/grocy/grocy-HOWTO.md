# Grocy — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/grocy:latest`. Household ERP (groceries, chores, batteries).

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:9283/` in a browser.

Default login: `admin` / `admin`

## Notes

- Port: 9283
- Data: `grocy_data` volume
- Track groceries, chores, batteries, equipment
- Barcode scanning via mobile app
