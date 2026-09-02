# GitLab CE — Existing Server Deploy Success

**Date:** 2026-09-02
**Server:** 46.224.127.228 (Ubuntu 26.04 LTS, 7.0GB RAM, Docker 29.6.1)
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
- Memory optimizations applied (2 Puma workers, Sidekiq concurrency 10, Prometheus disabled)

## Access

- **Web UI:** http://46.224.127.228:8082
- **SSH clone:** `ssh://git@46.224.127.228:2222/user/repo.git`
- **Username:** `root`
- **Password:** (stored in `.env` as `GITLAB_ROOT_PASSWORD`)

## Stacker Deploy Notes

The `stacker deploy --target server` command created the project in Stacker's backend (project ID: 634) but the container was not automatically started on the server. The compose file was generated correctly in `.stacker/deploy/default/docker-compose.remote.yml`.

**Workaround:** Deployed manually via SSH:
```bash
ssh -i ${BASE_PATH}/stacker-project-test root@46.224.127.228
mkdir -p /opt/gitlab && cd /opt/gitlab
# Copy compose file and run:
docker compose up -d
```

## Health Check Fix

The initial healthcheck format `"CMD curl -f ..."` failed with `/bin/sh: 1: CMD: not found`. Fixed to use `"CMD-SHELL curl -f ... || exit 1"` which works correctly.

## Verification

```
$ curl -s -o /dev/null -w '%{http_code}' http://46.224.127.228:8082/users/sign_in
200

$ docker ps --format '{{.Names}}\t{{.Status}}'
gitlab-app-1   Up X minutes (healthy)
```

## Container Status

```
CONTAINER       STATUS                  PORTS
gitlab-app-1    Up (healthy)            0.0.0.0:8082->80/tcp, 0.0.0.0:2222->22/tcp
```
