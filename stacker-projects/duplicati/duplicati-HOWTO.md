# Duplicati — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/duplicati:latest`. Encrypted backup solution.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8200/` in a browser.

## Notes

- Port: 8200
- Data: `duplicati_config` (settings), `duplicati_backups` (backup storage)
- Supports S3, B2, GDrive, OneDrive, SFTP, local filesystem
- AES-256 encryption built-in
