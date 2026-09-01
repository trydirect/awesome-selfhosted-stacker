# pipe-webhook-demo — PIPE test success (apprise → ntfy, webhook)

- **Date:** 2026-08-25
- **Deployment:** #849, server `pipe-webhook-demo-99e1` (id 602), Hetzner fsn1
- **IP:** 178.105.97.168
- Two apps co-located on one server: **apprise** (source, `:8000`) and
  **ntfy** (target/webhook sink, `:8080`).

## Feature added to make this possible
This CLI build's `pipe create` only supported endpoint **auto-discovery**
(openapi / html_forms / rest at standard paths) — apps like apprise (no
discoverable API) could not be a pipe source, and the manual-endpoint flags the
docs advertise were unimplemented. Added the documented non-interactive flags to
`pipe create` (Rust, `src/console/commands/cli/pipe.rs` + `src/bin/stacker.rs`):

```
--source-endpoint "METHOD /path"   --target-endpoint "METHOD /path"
--source-fields a,b                --target-fields a,b
--name <pipe-name>
```
When both endpoints are given, discovery is skipped entirely → works for any
app/URL and is fully scriptable.

## Commands (webhook pipe, manual trigger)
```bash
# 1. Create the pipe with explicit endpoints (no discovery)
stacker pipe create app ntfy \
  --source-endpoint "GET /status" --target-endpoint "POST /pipetest" \
  --source-fields message --target-fields message \
  --name apprise-to-ntfy --json
#   → instance eeba4c8e-…, field_mapping {"message":"$.message"}

# 2. Activate for manual triggering
stacker pipe activate eeba4c8e-… --trigger manual        # ✓ completed

# 3. Fire the webhook with a payload
stacker pipe trigger eeba4c8e-… --data '{"message":"hello from the apprise->ntfy pipe"}'
#   → ✓ completed, delivered: true, trigger_count 1

# 4. Inspect execution history
stacker pipe history eeba4c8e-…    # 78bbf89e… manual ✓ success
stacker pipe list                  # eeba4c8e… app → ntfy ● active  triggers=1 errors=0
```

## Verification (data actually reached the target)
```bash
curl "http://178.105.97.168:8080/pipetest/json?poll=1"
# {"event":"message","topic":"pipetest",
#  "message":"{\"message\":\"hello from the apprise->ntfy pipe\"}"}
```
The pipe POSTed the mapped payload to ntfy's `/pipetest` webhook and ntfy
published it — end-to-end PIPE delivery confirmed.

## Notes
- No proxy/HTTPS needed: pipe delivery is container-to-container over the
  internal Docker network (`http://project-ntfy-1:80/…`), plain HTTP.
- The stacker CLI change is uncommitted (left for review).
