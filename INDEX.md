# Project Index

Complete catalog of all `stacker-projects/` templates with status, ports, and
deployment notes. Generated alongside `README.md`.

## Stats

| Metric | Count |
|---|---|
| Total project templates | 266 |
| Deployed & verified (`LOCAL_DEPLOY_SUCCESS.md`) | 118 |
| Blocked / known-issue (`BUGS.md`) | 67 |
| Ready-to-deploy (no success file yet, scaffolded) | 75 |

> **Verified** = deployed to a clean server via `stacker deploy --target server`
> and confirmed (HTTP 200/30x or daemon running). **Blocked** = template exists
> but hits a documented blocker (image, port, or platform issue) — see the
> project's `BUGS.md`.

## Status Legend

- ✅ **verified** — deployed & confirmed working
- ⚠️ **blocked** — template present, deployment blocked (see `BUGS.md`)
- 🚧 **scaffolded** — config present, not yet deploy-verified

## Recently Added (Batch 20 — 2026-10-10/11)

| Project | Category | Port | Status | Notes |
|---|---|---|---|---|
| Actual Budget | Finance | 3000 | ✅ | image serves on :5006, mapped to :3000 |
| Akaunting | Accounting | 8080 | ✅ | + MariaDB; install redirect |
| Diun | Monitoring | — | ✅ | update-notifier daemon |
| Docker Socket Proxy | Security | 2375 | ✅ | restricted Docker API proxy |
| Docker Volume Backup | Backup | — | ✅ | scheduled volume backup daemon |
| FossBilling | Billing | 8083 | ✅ | + MariaDB; port 8083 (80 taken by caddy) |
| GLPI | ITSM | 8081 | ✅ | + MariaDB |
| Invoice Ninja | Invoicing | 8080 | ⚠️ | php-fpm only, no web server in image |
| LibreNMS | Monitoring | 8000 | ✅ | + MariaDB + redis |
| Netdata | Monitoring | 19999 | ✅ | real-time metrics dashboard |
| Ofelia | Scheduler | — | ✅ | Docker job scheduler daemon |
| CapRover | PaaS | 3000 | ✅ | fixed :80 conflict via BY_PASS_PROXY_CHECK |
| APITable | Database | 8084 | ⚠️ | upstream liquibase bug in image |
| Teable | Database | 3000 | ✅ | ghcr all-in-one + redis |
| Twenty | CRM | 3000 | ✅ | PG_DATABASE_URL + redis |
| Plane | Project mgmt | 8000 | ✅ | rabbitmq + minio + full env |
| LibreDesk | Helpdesk | 9000 | ✅ | full config.toml bind-mount |
| FreeScout | Helpdesk | 8082 | ✅ | mysql:8 (no pdo_pgsql in image) |

See the root `BUGS.md` for the full root-cause table. 6 of 7 batch-20 blocked
projects are now fixed & verified; only APITable remains blocked (upstream
liquibase bug).

---

*Full per-project index follows the same directory layout:*
`stacker-projects/<name>/{stacker.yml, .env.example, scripts/generate-secrets.sh}`.
