# Kopia — Stacker Deploy HOWTO

Single container: `kopia/kopia:latest`. Backup solution with deduplication and encryption.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:51515/` in a browser.

Login with the password from `.env`.

## Notes

- Port: 51515
- Data: `kopia_config`, `kopia_cache`, `kopia_logs` volumes
- Supports S3, B2, GCS, Azure, local filesystem backends
- Deduplication, compression, encryption built-in
