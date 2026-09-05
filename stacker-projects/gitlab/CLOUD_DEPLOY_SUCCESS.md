# GitLab CE — Cloud Deploy Success

**Date:** 2026-09-05
**Server:** 116.202.19.183 (Hetzner, fsn1, cpx32)
**GitLab Version:** 18.10.1-ce.0
**Deployment:** #275 — status: completed

## Deploy Command

```bash
cd stacker-projects/gitlab
./scripts/generate-secrets.sh
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN .env | cut -d= -f2)
stacker deploy --target cloud --key htz-8 --force-new
```

## Access

- **Web UI:** http://116.202.19.183:8082
- **SSH clone:** `ssh://git@116.202.19.183:2222/user/repo.git`
- **Username:** `root`
- **Password:** (stored in `.env` as `GITLAB_ROOT_PASSWORD`)

## Verification

```
$ curl -s -o /dev/null -w '%{http_code}' http://116.202.19.183:8082/users/sign_in
200

$ curl -s http://116.202.19.183:8082/users/sign_in | grep '<title>'
<title>Sign in · GitLab</title>

$ nc -z -w5 116.202.19.183 2222 && echo "SSH port open"
SSH port open
```

## Key Fixes Applied

1. **Port quoting:** `2222:22` quoted to prevent YAML 1.1 sexagesimal parsing (`2222*60+22 = 133342`)
2. **Backend port renderer:** Fixed to preserve quotes on port mappings
3. **GITLAB_OMNIBUS_CONFIG:** Single-line semicolon-separated format in `.env`
