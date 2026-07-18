# Stirling-PDF — Stacker Deploy HOWTO

Single container: `frooodle/s-pdf:latest`. No database needed.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8080/` in a browser.

## Features

- Merge, split, compress, convert PDFs
- OCR, watermark, encrypt/decrypt
- Rotate, crop, resize pages
- Convert images to PDF and back

## Notes

- Port: 8080
- Volumes: `stirling_data` (OCR/tessdata), `stirling_config` (settings)
- No secrets needed
