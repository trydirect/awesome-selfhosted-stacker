# duplicati — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-20

## Commands used

```bash
cd stacker-projects/duplicati
chmod +x scripts/generate-secrets.sh   # wasn't executable
./scripts/generate-secrets.sh
stacker deploy --target local --force-rebuild
```

`stacker.yml`/`.env.example`/`generate-secrets.sh` never set
`SETTINGS_ENCRYPTION_KEY`, which `lscr.io/linuxserver/duplicati` requires
— container started but refused to serve:
```
*** Missing encryption key, unable to encrypt your settings database ***
*** Please set a value for SETTINGS_ENCRYPTION_KEY and recreate the container ***
```
Fixed by adding `SETTINGS_ENCRYPTION_KEY: "${SETTINGS_ENCRYPTION_KEY}"` to
`app.environment`, generating it in `generate-secrets.sh`, and adding it
to `.env.example`. See `BUGS.md`.

Also hit the "stale compose file" trap: after editing `stacker.yml`,
`stacker deploy --target local` reused the old `.stacker/docker-compose.yml`
(logged "Using existing .stacker/docker-compose.yml") and the new env var
never made it into the container until re-running with `--force-rebuild`.
Not a bug — expected caching behavior — but worth remembering when
iterating on `stacker.yml` env vars locally.

## Verification

- `docker exec stacker-app-1 env | grep SETTINGS_ENCRYPTION_KEY` → present
  with the generated value.
- `curl -I http://localhost:8200/` → `HTTP/1.1 200 OK`, `Server: Kestrel`
  (Duplicati's web UI backend).

No remaining bugs blocking local deploy once `SETTINGS_ENCRYPTION_KEY` was
added and the compose file was rebuilt.
