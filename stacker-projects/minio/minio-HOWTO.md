# MinIO — Stacker Deploy HOWTO

Single container: `minio/minio:latest`. S3-compatible object storage.

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

- API: `http://<SERVER_IP>:9000/`
- Console: `http://<SERVER_IP>:9001/`

Login with credentials from `.env`.

## Notes

- Port: 9000 (S3 API), 9001 (web console)
- Data: `minio_data` volume
- S3-compatible — works with AWS SDK, rclone, s3cmd
- Create buckets and access keys via the console
