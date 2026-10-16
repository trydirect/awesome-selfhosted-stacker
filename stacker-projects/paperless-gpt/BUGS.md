# paperless-gpt — known issues

## [BUG] Image tag `ghcr.io/paperless-ngx/paperless-ngx:v3.3.1` did not exist (404)

**Severity:** High (deploy failed at image pull)
**Date:** 2026-10-16
**Status:** FIXED 2026-10-16 — pinned `ghcr.io/paperless-ngx/paperless-ngx:3.3.1`

paperless-ngx publishes GHCR tags **without** the `v` prefix
(`3.3.1` exists, `v3.3.1` / `v3.3.0` do not). The other template images were
already correct (`icereed/paperless-gpt:v0.31.0` uses the `v` prefix).

## [BUG] Empty OPENAI_API_KEY crash-loops the app at startup

**Severity:** Medium (deploy "succeeds" but the app is unusable)
**Date:** 2026-10-16
**Status:** workaround documented; no template change

### Actual
```
level=fatal msg="Please set the OPENAI_API_KEY environment variable for OpenAI provider."
```
`.env.example` documents `OPENAI_API_KEY` as "LLM configuration
(user-supplied)", but nothing validates it before deploy — an empty value
passes compose generation and the app restart-loops after the deploy reports
success.

### Workaround
Set `OPENAI_API_KEY` in `.env` before `stacker deploy` (a placeholder satisfies
the startup check; a real key is needed for actual LLM calls).

### Suggested improvements
- `generate-secrets.sh`: warn (or fail) when `OPENAI_API_KEY` is empty and
  `LLM_PROVIDER=openai`.
- Or document in the project README that the stack requires a user-supplied
  key to start.

## Related CLI issue (root BUGS.md)
Redeploy reuses the cached `.stacker/docker-compose.yml` — env changes in
`.env` do not propagate until `.stacker/` is removed (`rm -rf .stacker` before
redeploy). This cost deployments #1368/#1369 before #1370 succeeded.
