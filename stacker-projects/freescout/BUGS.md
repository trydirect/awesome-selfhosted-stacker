# [BUG] freescout (bfren/freescout) s6 stack exits after boot

## Status: BLOCKED

## Summary
bfren/freescout:latest starts its s6 overlay services (nginx, php) but then
shuts them all down cleanly and the container enters a restart loop. No clear
error in the forwarded logs.

## Root cause
Unclear from logs. The s6 \`init\` service stops, cascading nginx/php shutdown.
Likely a missing required env (e.g. DB creds for the embedded installer) that
the image treats as fatal without logging.

## Expected
nginx stays up and serves the FreeScout installer.

## Actual
\`status=restarting\`, s6-rc reports services \"successfully stopped\" then the
container exits.

## Workaround
Use the official \`freescout/freescout\` image (if published) or provide the
full set of DB_* env vars the bfren image expects. Not diagnosable from the
image's own logs alone.

## Reproduction
```bash
cd stacker-projects/freescout
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-10
