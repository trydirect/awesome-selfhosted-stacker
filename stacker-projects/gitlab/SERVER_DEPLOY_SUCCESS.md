# GitLab CE — Existing Server Deploy Success

**Date:** 2026-09-03
**Server:** 46.224.127.228 (Ubuntu 26.04 LTS, 18.0GB RAM, Docker 29.6.1)
**GitLab Version:** 18.10.1-ce.0

## Deploy Command

```bash
cd stacker-projects/gitlab
./scripts/generate-secrets.sh
stacker deploy --target server
```

## What was deployed

- **GitLab CE** omnibus container (`gitlab/gitlab-ce:18.10.1-ce.0`)
- Single container with bundled PostgreSQL, Redis, Nginx, Puma, Sidekiq
- Persistent volumes: `gitlab_config`, `gitlab_logs`, `gitlab_data`
- Config via `gitlab.rb` bind mount (not `GITLAB_OMNIBUS_CONFIG` env var)

## Access

- **Web UI:** http://46.224.127.228:8082
- **SSH clone:** `ssh://git@46.224.127.228:2222/user/repo.git`
- **Username:** `root`
- **Password:** (stored in `.env` as `GITLAB_ROOT_PASSWORD`)

## Key Design Decisions

### gitlab.rb instead of GITLAB_OMNIBUS_CONFIG

The `GITLAB_OMNIBUS_CONFIG` multiline environment variable caused `invalid containerPort: 133342` errors when serialized through Stacker's compose pipeline. Single quotes inside the YAML value break Docker Compose parsing.

**Fix:** Use a `gitlab.rb` config file mounted as a bind mount at `/etc/gitlab/gitlab.rb:ro`. This avoids all quoting issues.

### Healthcheck format

Must use `CMD-SHELL` not `CMD` for string-form healthchecks:
```yaml
healthcheck:
  test: "CMD-SHELL curl -f http://localhost/-/health || exit 1"
```

## Verification

```
$ curl -s -o /dev/null -w '%{http_code}' http://46.224.127.228:8082/users/sign_in
200

$ docker ps --format '{{.Names}}\t{{.Status}}'
gitlab-app-1   Up X minutes (healthy)
```

## Known Issues

- `stacker deploy --target server` fails with "SSH key is not available" due to Vault storage errors. Workaround: manually add SSH key to server and deploy via SSH.
- `stacker deploy --target cloud --force-new` fails with "SSH key status is 'none', not active" — Stacker backend SSH key provisioning bug.
