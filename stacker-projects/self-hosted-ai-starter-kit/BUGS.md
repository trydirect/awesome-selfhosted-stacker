# self-hosted-ai-starter-kit — known issues

## [BUG] Deploy reports `paused [internal_error]` while the stack deploys fine

**Severity:** Medium (false failure — breaks automation/success criteria)
**Date:** 2026-10-16

### Steps
1. `stacker deploy --target server` (target 46.224.127.228).

### Actual
```
✗ Deployment #1372 ended as 'paused' [internal_error]
✗ Deployment #1373 ended as 'paused' [internal_error]   (retry)
```
Server-side state after #1373: all four containers `Up (healthy)`
(n8n, postgres, ollama, qdrant); `curl localhost:5678/healthz` →
`{"status":"ok"}`, root → 200. After #1372 alone the side services were up
and `project-app-1` (n8n) was still missing — the retry completed the stack.

### Expected
Deployment watch reports success when all services are healthy.

### Notes
- Platform-side classification problem (also logged to root BUGS.md).
- Per the CLI message ("Redeploying will retry") a single retry is the
  documented remediation; no further retries were made after the repeat.
- The template itself is fine — stack verified working on the server.
