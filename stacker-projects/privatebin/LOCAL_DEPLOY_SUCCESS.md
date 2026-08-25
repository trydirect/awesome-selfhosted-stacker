# privatebin — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-19

## Commands used

```bash
cd stacker-projects/privatebin
./scripts/generate-secrets.sh
stacker deploy --target local
```

As expected from the already-documented collision bug
([stacker#235](https://github.com/trydirect/stacker/issues/235), see
`shlink/BUGS.md`), this reused the shared `stacker` Compose project and
flagged the previous project's `stacker-postgres-1` as an orphan — no new
investigation needed, privatebin itself doesn't use a database so it was
unaffected.

## Verification

- `docker ps` → `stacker-app-1` (privatebin/nginx-fpm-alpine:latest) up,
  `0.0.0.0:8080->8080/tcp`.
- `curl -I http://localhost:8080/` → `HTTP/1.1 200 OK` (nginx, PrivateBin
  UI page).
- `curl -X POST http://localhost:8080/ -H "X-Requested-With: JSONHttpRequest"`
  with a malformed paste payload → `{"status":1,"message":"Invalid data."}`,
  then a second rapid request → `{"status":1,"message":"Please wait 10
  seconds between each post."}` — confirms the PHP backend is live,
  parsing JSON, validating paste structure, and enforcing its rate limiter.
  A fully valid encrypted-paste round trip wasn't attempted further since
  it requires replicating PrivateBin's client-side AES-GCM encryption
  (browser JS), which is out of scope for CLI verification; UI load +
  live/correctly-behaving API is sufficient evidence of a working stack.

No stacker or privatebin bugs beyond the already-documented local-deploy
collision issue.
