# RustFS — Stacker Example

[RustFS](https://github.com/rustfs/rustfs) is an S3-compatible object storage server written in Rust.

## Deploy locally

```bash
# 1. Set credentials
cat > .env <<'EOF'
RUSTFS_ACCESS_KEY=rustfsadmin
RUSTFS_SECRET_KEY=rustfsadmin
EOF

# 2. Deploy
stacker deploy --target local
```

## Access

| Service | URL |
|---------|-----|
| S3 API | http://localhost:9000 |
| Web Console | http://localhost:9001 |

Login with the credentials from your `.env` file.

## Status & logs

```bash
stacker status
docker compose -f .stacker/docker-compose.yml logs -f app
or
stacker logs
```

## Stop

```bash
docker compose -f .stacker/docker-compose.yml down
```

## Notes

- `RUSTFS_UNSAFE_BYPASS_DISK_CHECK=true` is set so all four data directories (`/data/rustfs0`–`3`) can share a single host disk. Remove this for production.
- TLS is disabled for local deployment. RustFS enables TLS when `RUSTFS_TLS_PATH` points to a directory containing valid certificates.
- OpenTelemetry collector sidecar runs on port `4318` for optional metrics/tracing.
