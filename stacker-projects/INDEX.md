# Stacker Self-Hosted Projects — Full Index

**248 projects** · **122 tested & verified** · Updated 2026-08-31

Each project is a ready-to-run `stacker.yml` deployment. See [README.md](../README.md) for quick start.

## Proxy Support

Stacker supports multiple reverse proxy types for automatic HTTPS and domain routing:

| Type | Image | Auto-HTTPS | Notes |
|------|-------|------------|-------|
| `traefik` | traefik:latest | ✅ (Let's Encrypt) | Default for cloud deploys |
| `caddy` | caddy:2-alpine | ✅ (automatic) | Simple config, zero-touch TLS |
| `nginx-proxy-manager` | jc21/nginx-proxy-manager | ✅ (Let's Encrypt) | GUI-based management |
| `nginx` | nginx:alpine | ❌ | Manual config |
| `none` | — | — | No proxy (direct port access) |

Configure in `stacker.yml`:
```yaml
proxy:
  type: caddy  # or: traefik, nginx-proxy-manager, nginx, none
  domains:
    - domain: app.example.com
      ssl: off
      upstream: app:3000
```

## Secret Management

Generate secrets with `./scripts/generate-secrets.sh` or use the Stacker CLI:

```bash
stacker secrets list                    # list local .env secrets
stacker secrets validate                # check all ${VAR} refs are set
stacker secrets set KEY --scope service --service my-app --body "value"  # remote Vault
```

---

## AI & LLM (9)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| ai-knowledge-base | langgenius/dify-api, qdrant/qdrant | 8080 | postgres, qdrant | ✅ |
| ai-automation-workflows | flowiseai/flowise, n8nio/n8n | 3000 | postgres | ✅ |
| ollama-local | ollama/ollama | 11434 | — | |
| private-sovereign-ai | ghcr.io/open-webui/open-webui | 3000 | — | ✅ |
| anythingllm | mintplexlabs/anythingllm | 3001 | — | |
| langflow | langflowai/langflow | 7860 | postgres | |
| localai | localai/localai | 8080 | — | ✅ |
| khoj | ghcr.io/khoj-ai/khoj | 42110 | postgres | |
| lobechat | lobehub/lobe-chat | 3210 | postgres | |

## Analytics (21)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| aptabase | ghcr.io/aptabase/aptabase | 3000 | postgres, clickhouse | |
| countly-server | bitnami/nginx | 8080 | mongodb | |
| d8a | ghcr.io/d8a-tech/d8a | 3000 | — | ✅ |
| daily-stars-explorer | ghcr.io/emanuelef/daily-stars-explorer | 8080 | — | ✅ |
| druid | apache/druid:31.0.0 | 8888 | postgres, zookeeper | ✅ |
| goaccess | nginx:1.27-alpine | 8080 | — | |
| goatcounter | arp242/goatcounter | 8080 | — | |
| hitkeep | ghcr.io/pascalebeier/hitkeep | 8080 | — | |
| matomo | matomo | 8080 | mariadb | |
| metabase | metabase/metabase | 3000 | postgres | ✅ |
| middleware | middlewareeng/middleware | 3333 | postgres | |
| offen | offen/offen | 3000 | — | |
| plausible | ghcr.io/plausible/community-edition | 8000 | postgres, clickhouse | ✅ |
| posthog | posthog/posthog | 8000 | postgres, redis | ✅ |
| redash | redash/redash | 5000 | postgres, redis | ✅ |
| rybbit | ghcr.io/rybbit-io/rybbit-client | 3002 | clickhouse, postgres, redis | ✅ |
| statistics-for-strava | robiningelbrecht/strava-statistics | 8081 | — | ✅ |
| supabase-posthog | kong/kong:3.9.1 | 8000 | postgres | |
| superset | apache/superset | 8088 | postgres, redis | ✅ |
| umami | ghcr.io/umami-software/umami | 3000 | postgres | ✅ |
| shaper | taleshape/shaper | 8080 | — | |

## Automation (19)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| activepieces | ghcr.io/activepieces/activepieces | 8080 | postgres, redis | ✅ | |
| automatisch | automatisch/automatisch | 3000 | postgres | | |
| calcom | calcom/cal.com | 3000 | postgres | ✅ | |
| changedetection | ghcr.io/dgtlmoon/changedetection.io | 5000 | — | ✅ | |
| dify | (static) | — | — | | |
| homeassistant | lscr.io/linuxserver/homeassistant | 8123 | — | | |
| n8n | n8nio/n8n | 5678 | postgres | ✅ | |
| rallly | lukevella/rallly | 3000 | postgres | | |
| typebot | baptistearno/typebot-builder | 3001 | postgres | | |
| vikunja | (Dockerfile) | 3456 | postgres | ⚠️ | |
| apache-airflow | apache/airflow | 8080 | postgres | | DB migrate |
| dagu | ghcr.io/dagucloud/dagu | 8080 | — | | |
| dittofeed | dittofeed/dittofeed | 3000 | postgres, clickhouse, kafka | | Auto-migrate |
| huginn | ghcr.io/huginn/huginn | 3000 | postgres | | DB migrate+seed |
| kestra | kestra/kestra | 8080 | postgres | | |
| windmill | ghcr.io/windmill-labs/windmill | 8000 | postgres | ✅ | |
| cronicle | cronicle/cronicle | 3012 | — | | |

## Backup (2)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| urbackup | uroni/urbackup-server | 55414 | — | | |
| restic-rest-server | restic/rest-server | 8000 | — | | |

## Bookmarks & Link Sharing (7)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| ArchiveBox | archivebox/archivebox | 8000 | — | |
| freshrss | lscr.io/linuxserver/freshrss | 8080 | — | ✅ |
| linkding | sissbruecker/linkding | 9090 | — | ✅ |
| linkwarden | ghcr.io/linkwarden/linkwarden | 3000 | postgres | ✅ |
| wallabag | wallabag/wallabag | 80 | postgres, redis | |
| karakeep | ghcr.io/karakeep-app/karakeep | 3000 | postgres, meilisearch | | Auto-migrate |
| readeck | codeberg.org/readeck/readeck | 8000 | postgres | | Auto-migrate |

## CMS & Blogging (8)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| bookstack | lscr.io/linuxserver/bookstack | 6875 | mariadb | ✅ |
| directus | directus/directus | 8055 | postgres | ✅ |
| ghost | ghost:5-alpine | 2368 | mysql | ✅ |
| outline | outlinewiki/outline | 3000 | postgres, redis | ✅ |
| strapi | naskio/strapi | 1337 | postgres | ✅ |
| wordpress | wordpress | 8080 | mysql | ✅ |
| wordpress-matomo | wordpress | 8080 | mysql, mariadb | |
| writefreely | writeas/writefreely | 8080 | mysql | ✅ |

## Communication (16)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| AstrBot | soulter/astrbot | 6185 | — | ✅ | |
| chatwoot | chatwoot/chatwoot | 3000 | postgres, redis | ✅ | |
| discourse | discourse/discourse | 80 | postgres, redis | ✅ | |
| gotify | gotify/server | 8080 | — | | |
| jitsi | jitsi/web:unstable | 80 | — | ✅ | |
| librechat | ghcr.io/danny-avila/librechat | 3080 | mongo | | |
| mattermost | mattermost/mattermost-enterprise-edition | 8065 | postgres | | |
| rocket-chat | rocket.chat | 3000 | mongo | ✅ | |
| screego | ghcr.io/screego/server | 5050 | — | | |
| synapse | matrixdotorg/synapse | 8008 | postgres | ✅ | |
| listmonk | listmonk/listmonk | 9000 | postgres | ✅ | |
| zulip | zulip/docker-zulip | 80 | postgres | | |
| element | vectorim/element-web | 8080 | — | | |
| ntfy | binwiederhier/ntfy | 8080 | — | ✅ | |
| anycable | anycable/anycable-go | 8080 | — | | |
| centrifugo | centrifugo/centrifugo | 8000 | — | | |
| apprise | caronc/apprise | 8000 | — | ✅ | |

## Design (1)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| penpot | penpotapp/penpot-frontend | 9001 | postgres, redis | |

## Dashboard (5)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| appsmith | appsmith/appsmith-ce | 80 | — | |
| dashy | lissy93/dashy | 8082 | — | ✅ |
| grist | gristlabs/grist | 8484 | — | ⚠️ |
| homer | b4bz/homer | 8080 | — | |
| organizr | organizr/organizr | 9983 | — | |

## Developer & DevOps Tools (20)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| caddy | caddy | 80 | — | | |
| code-server | lscr.io/linuxserver/code-server | 8443 | — | | |
| cyberchef | ghcr.io/gchq/cyberchef | 8000 | — | ✅ | |
| floci | floci/floci | 4566 | — | ✅ | |
| gitness | harness/gitness | 3000 | — | ✅ | |
| gitea | gitea/gitea | 3000 | postgres | ✅ | |
| hermes-agent | (Dockerfile) | 8000 | — | | |
| insforge | (node) | 7130 | — | | |
| it-tools | corentinth/it-tools | 8083 | — | ✅ | |
| network-tools | trydirect/network-tools | — | — | | |
| nocodb | nocodb/nocodb | 8080 | postgres | ✅ | |
| semaphore | semaphoreui/semaphore | 3000 | postgres | ✅ | |
| supabase | kong/kong:3.9.1 | 8000 | postgres | ✅ | |
| traefik | traefik:v3.0 | 80 | — | | |
| wireguard | lscr.io/linuxserver/wireguard | 51820 | — | | |
| woodpecker-ci | woodpeckerci/woodpecker-server | 8000 | — | | |
| olivetin | jamesread/olivetin | 1337 | — | ✅ | |
| appwrite | appwrite/appwrite | 80 | mariadb, redis | | Auto-migrate |
| budibase | budibase/budibase | 80 | couchdb, redis | | |
| prowlarr | linuxserver/prowlarr | 9696 | — | | |

## Document Management (10)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| archivesspace | archivesspace/archivesspace | 8080 | mysql, solr | ✅ |
| docmost | docmost/docmost | 3000 | postgres, redis | ✅ |
| mail-archiver | s1t5/mailarchiver | 5000 | postgres | |
| openarchiver | logiclabshq/open-archiver | 3000 | postgres, valkey, meilisearch | |
| onlyoffice | onlyoffice/documentserver | 80 | — | |
| paperless-ngx | ghcr.io/paperless-ngx/paperless-ngx | 8000 | postgres, redis | ✅ |
| stirling-pdf | frooodle/s-pdf | 8080 | — | ✅ |
| outline | outlinewiki/outline | 3000 | postgres, redis | ✅ |
| wikijs | ghcr.io/requarks/wiki | 3000 | postgres | |
| kopia | kopia/kopia | 51515 | — | ✅ |

## File Management (11)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| duplicati | lscr.io/linuxserver/duplicati | 8200 | — | ✅ | |
| filebrowser | filebrowser/filebrowser | 8080 | — | ✅ | |
| minio | minio/minio | 9000 | — | | |
| nextcloud | nextcloud | 8080 | mariadb, redis | ✅ | |
| pingvin-share | stonith404/pingvin-share | 3000 | — | ✅ | |
| rustfs | rustfs/rustfs | 9000 | — | ✅ | |
| s4core | s4core/s4core | 9000 | — | ✅ | |
| syncthing | lscr.io/linuxserver/syncthing | 8384 | — | | |
| zipline | ghcr.io/diced/zipline | 3000 | postgres | | Auto-migrate |

## Media (25)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| audiobookshelf | ghcr.io/advplyr/audiobookshelf | 13378 | — | | |
| bitmagnet | ghcr.io/bitmagnet-io/bitmagnet | 3333 | postgres | | |
| calibre-web | linuxserver/calibre-web | 8083 | — | | |
| comfyui | ashleykza/comfyui | 8188 | — | | |
| frigate | ghcr.io/blakeblackshear/frigate | 5000 | — | | |
| ganymede | ghcr.io/zibbp/ganymede | 4800 | postgres | ✅ | |
| immich | ghcr.io/immich-app/immich-server | 2283 | postgres, redis | ✅ | |
| jellyfin | jellyfin/jellyfin | 8096 | — | ✅ | |
| jellyseerr | fallenbagel/jellyseerr | 5055 | — | | |
| kavita | lscr.io/linuxserver/kavita | 5000 | — | ✅ | |
| komga | gotson/komga | 25600 | — | ✅ | |
| metube | alexta69/metube | 8081 | — | ✅ | |
| navidrome | deluan/navidrome | 4533 | — | ✅ | |
| ombi | lscr.io/linuxserver/ombi | 3579 | — | | |
| peertube | chocobozzz/peertube | 9000 | postgres, redis | | |
| romm | rommapp/romm | 8080 | mariadb | ✅ | |
| swarm-ui | (Dockerfile) | 7801 | — | | |
| tautulli | lscr.io/linuxserver/tautulli | 8181 | — | ✅ | |
| castopod | castopod/app | 8000 | mysql | | Auto-create |
| funkwhale | funkwhale/all-in-one | 5000 | postgres, redis | | DB migrate |
| ampache | ampache/ampache | 8080 | mysql | | Auto-create |
| emby | emby/embyserver | 8096 | — | | |
| sonarr | linuxserver/sonarr | 8989 | — | | |
| radarr | linuxserver/radarr | 7878 | — | | |
| lidarr | linuxserver/lidarr | 8686 | — | | |

## Booking & Scheduling (2)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| easyappointments | alextselegidis/easyappointments | 8080 | mysql | | Auto-create |
| librebooking | ghcr.io/librebooking/librebooking | 8080 | mysql | | Auto-create |

## Calendar & Contacts (2)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| radicale | tomsquest/docker-radicale | 5232 | — | | |
| baikal | ckulka/baikal | 8080 | — | | |

## Email (2)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| simplelogin | simplelogin/app | 8080 | postgres | | DB migrate |
| stalwart-mail | stalwartlabs/mail-server | 8080 | — | | Built-in DB |

## Events (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| hi-events | ghcr.io/hidevops/hi-events | 8080 | postgres, redis | | DB migrate |

## Monitoring (11)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| crowdsec | crowdsecurity/crowdsec | — | — | | |
| glances | nicolargo/glances:latest-full | 61208 | — | ✅ | |
| goaccess | nginx:1.27-alpine | 8080 | — | | |
| grafana | grafana/grafana | 3000 | — | ✅ | |
| pihole | pihole/pihole | 8080 | — | ✅ | |
| speedtest-tracker | lscr.io/linuxserver/speedtest-tracker | 8080 | — | | |
| stackdog | trydirect/stackdog | 5000 | — | ✅ | |
| uptimekuma | louislam/uptime-kuma:2 | 3001 | — | ✅ | |
| healthchecks | healthchecks/healthchecks | 8000 | postgres | | Auto-migrate |
| cachet | cachethq/cachet | 8000 | postgres, redis | | DB migrate |

## Money & Budgeting (3)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| btcpay-server | btcpayserver/btcpayserver | 23000 | postgres | | |
| firefly-iii | fireflyiii/core | 8080 | postgres | | |
| ghostfolio | ghostfolio/ghostfolio | 3333 | postgres, redis | | |

## Note-taking (5)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| hedgedoc | quay.io/hedgedoc/hedgedoc | 3000 | postgres | ✅ | |
| memos | ghcr.io/usememos/memos | 5230 | — | | |
| trilium | zadam/trilium | 8081 | — | ✅ | |
| standard-notes | standardnotes/server | 3000 | postgres, redis | | Auto-migrate |
| appflowy | appflowyinc/appflowy_cloud | 8000 | postgres, redis | | Auto-migrate |

## Password Management (13)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| bitwarden | vaultwarden/server | 80 | postgres | |
| cryptpad | cryptpad/cryptpad | 3000 | — | |
| hanko | ghcr.io/teamhanko/hanko | 8000 | postgres | ✅ |
| infisical | infisical/infisical | 8080 | postgres | ✅ |
| keycloak | quay.io/keycloak/keycloak | 8080 | postgres | |
| onetimesecret | onetimesecret/onetimesecret | 3000 | redis | ✅ |
| passbolt | passbolt/passbolt_api | 443 | mariadb | |
| vaultwarden | vaultwarden/server | 8080 | — | ✅ |
| vaultwarden-traefik | vaultwarden/server | 80/443 | — | ✅ |
| vaultwarden-caddy | vaultwarden/server | 80/443 | — | ✅ |
| vaultwarden-npm | vaultwarden/server | 80/443 | — | ✅ |
| vaultwarden-secrets | vaultwarden/server | 8080 | — | ✅ |
| zitadel | ghcr.io/zitadel/zitadel | 8080 | postgres, redis | ✅ |

> **`vaultwarden-*` are feature-test variants** of a single vaultwarden base,
> each exercising one Stacker capability end-to-end: `-traefik`/`-caddy`/`-npm`
> reverse-proxy routing (`vault.example.com → app:80`), and `-secrets` the
> `stacker secrets` workflow (`ADMIN_TOKEN` in a local `.env`). See
> [vaultwarden-caddy/README.md](vaultwarden-caddy/README.md) for the commands.

## Project Management (4)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| huly | ghcr.io/hcengineering/platform | 8080 | postgres, redis | | |
| openproject | openproject/community | 8080 | postgres | | |
| focalboard | mattermost/focalboard | 8000 | postgres | | Auto-migrate |
| planka | ghcr.io/plankanban/planka | 1337 | postgres | | Auto-migrate |

## Maps & GPS (2)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| dawarich | freika/dawarich | 3000 | postgres, redis | | |
| traccar | traccar/traccar | 8082 | postgres | | Auto-migrate |

## Office Suites (2)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| etherpad | etherpad/etherpad | 9001 | — | |
| onlyoffice | onlyoffice/documentserver | 80 | — | |

## Photo Management (2)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| photoprism | photoprism/photoprism | 2342 | — | ✅ | |
| lychee | lycheeorg/lychee | 8080 | postgres | | Auto-migrate |

## Recipe & Lifestyle (3)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| grocy | lscr.io/linuxserver/grocy | 9283 | — | ✅ |
| mealie | ghcr.io/mealie-recipes/mealie | 9925 | — | ✅ |
| tandoor | vabene1111/recipes | 8080 | postgres | ✅ |

## Search (6)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| meilisearch | getmeili/meilisearch | 7700 | — | ✅ | |
| searxng | searxng/searxng | 8080 | — | | |
| whoogle | benbusby/whoogle-search | 5000 | — | | |
| typesense | typesense/typesense:27.1 | 8108 | — | | |
| opensearch | opensearchproject/opensearch | 9200 | — | | |
| manticore | manticoresearch/manticore | 9306 | — | | |

## Databases (4)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| clickhouse | clickhouse/clickhouse-server | 8123 | — | | |
| surrealdb | surrealdb/surrealdb | 8000 | — | | |
| influxdb | influxdb:2.7 | 8086 | — | ✅ | |
| mongodb | mongo:7 | 27017 | — | | |

## Storage (3)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| seaweedfs | chrislusf/seaweedfs | 8888 | — | | |
| seafile | seafileltd/seafile-mc | 8080 | mysql | | |
| filestash | machines/filestash | 8334 | — | | |

## Feed Readers (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| miniflux | miniflux/miniflux | 8080 | postgres | | Auto-migrate |

## DNS (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| adguard-home | adguard/adguardhome | 3000 | — | | |

## Database Management (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| baserow | baserow/baserow | 80 | postgres, redis | | Auto-migrate |

## IoT (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| node-red | nodered/node-red | 1880 | — | | |

## Health & Fitness (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| wger | wger/server | 8000 | postgres | | Auto-migrate |

## Pastebins (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| privatebin | privatebin/nginx-fpm-alpine | 8080 | — | | |

## URL Shorteners (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| shlink | shlinkio/shlink | 8080 | postgres | | Auto-migrate |

## Time Tracking (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| kimai | kimai/kimai2 | 8001 | mysql | | DB migrate+seed |

## VPN (3)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| netbird | netbirdio/management | 33073 | postgres | | Auto-migrate |
| firezone | firezone/firezone | 8080 | postgres | | DB migrate |
| headscale | headscale/headscale | 8080 | — | | |

## Miscellaneous (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| moodist | ghcr.io/remvze/moodist | 8080 | — | | |

## Games (2)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| crafty-controller | registry.gitlab.com/crafty-controller/crafty-4 | 8443 | — | | |
| pterodactyl | ghcr.io/pterodactyl/panel | 80 | mysql, redis | | DB migrate+seed |

## CRM (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| espocrm | espocrm/espocrm | 8080 | mysql | | |

## Static Site Generators (1)

| Project | Image | Port | DB | Tested | Notes |
|---------|-------|------|----|:------:|-------|
| hugo | klakegg/hugo | 1313 | — | | |

## Self-hosting (4)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| arcane | ghcr.io/getarcaneapp/manager | 3552 | — | ✅ |
| coolify | coollabsio/coolify | 8000 | postgres, redis | |
| dockhand | fnsys/dockhand | 3000 | — | ✅ |
| portainer | portainer/portainer-ce | 9000 | — | |

## Social (7)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| discourse | discourse/discourse | 80 | postgres, redis | ✅ |
| lemmy | dessalines/lemmy:0.19.11 | 8536 | postgres | ✅ |
| mastodon | ghcr.io/mastodon/mastodon | 3000 | postgres, redis | ✅ |
| postiz-app | ghcr.io/gitroomhq/postiz-app | 4007 | postgres, redis, elasticsearch | ✅ |
| socioboard | sintelli/socioboard-web | 80 | mysql, mongo | |

## Surveys (1)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| limesurvey | misterunknown/limesurvey | 80 | mariadb | |

## Email - Webmail (1)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| roundcube | roundcube/roundcubemail | 80 | — | |

## Ticketing (1)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| zammad | zammad/zammad | 80 | postgres, redis | |

## Video Streaming (1)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| peertube | chocobozzz/peertube | 9000 | postgres, redis | |

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Tested & verified on server |
| ⚠️ | Works with documented workaround |
| (empty) | Configured, not yet re-deployed |
| — | Not applicable |

## Structure

Every project follows:

```
project-name/
  stacker.yml               # deployment config
  .env.example              # public config template (where present)
  .env                      # secrets (gitignored)
  scripts/generate-secrets.sh   # secret generator (where present)
```

See [README.md](../README.md) for deployment instructions.
