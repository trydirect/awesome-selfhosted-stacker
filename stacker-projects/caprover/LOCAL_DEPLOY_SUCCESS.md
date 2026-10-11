# CapRover — Local Deploy Success

## Result: SUCCESS

- **Image:** `caprover/cap:latest`
- **Host port:** 3000
- **Deployments:** #1342, #1343
- **Verified:** HTTP 200

## Fix applied

Port 80 conflict with Stacker's always-on caddy ingress resolved:
- Removed host-port `80:80` (installer self-check no longer needs it).
- Added `BY_PASS_PROXY_CHECK=TRUE` so the installer's :80 self-check is skipped.
- Added `MAIN_NODE_IP_ADDRESS=127.0.0.1` to avoid the installer probing a
  public IP that caddy already owns.

## Commands used
```bash
cd stacker-projects/caprover
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test --force-rebuild
```

## Verification
- `curl -o /dev/null -w "%{http_code}" http://46.224.127.228:3000/` → `200`.
- Dashboard reachable on :3000.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-11
