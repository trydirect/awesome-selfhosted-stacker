# Meilisearch — Stacker Deploy HOWTO

Single container: `getmeili/meilisearch:latest`. Lightning-fast search engine with typo tolerance.

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

Open `http://<SERVER_IP>:7700/` in a browser.

## Notes

- Port: 7700
- Data: `meilisearch_data` volume
- Instant search with typo tolerance
- REST API for indexing and searching
- Supports faceted search, filters, pagination
