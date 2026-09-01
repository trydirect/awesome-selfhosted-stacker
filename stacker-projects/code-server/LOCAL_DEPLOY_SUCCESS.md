# code-server — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-20

## Commands used

```bash
cd stacker-projects/code-server
chmod +x scripts/generate-secrets.sh   # wasn't executable in the repo checkout
./scripts/generate-secrets.sh
stacker deploy --target local
```

`stacker.yml` had no `env_file:` key at all, so `.env` was never loaded
and `${CODE_SERVER_PASSWORD}`/`${CODE_SERVER_SUDO_PASSWORD}` substitution
failed immediately (`Error: Environment variable not found:
$CODE_SERVER_PASSWORD`) even though the values were correctly generated
into `.env`. Fixed (with user confirmation) by adding `env_file: .env` to
`stacker.yml`, matching every other project's pattern. See `BUGS.md`.

## Verification

- `docker ps` → `stacker-app-1` (lscr.io/linuxserver/code-server:latest)
  up, `0.0.0.0:8443->8443/tcp`.
- `curl -I http://localhost:8443/` → `302 Found` → `./login` (auth
  correctly enforced).
- Full login round trip: fetched login page for CSRF cookie, POSTed
  `password` + `_csrf` with the generated `CODE_SERVER_PASSWORD` →
  `302 Found` to `./` with a valid `code-server-session` cookie.
- Authenticated request to `/` → redirects to
  `./?folder=/config/workspace`, matching the configured
  `DEFAULT_WORKSPACE: /config/workspace`.

No remaining bugs blocking local deploy once `env_file` was added.
