# Stacker Self-Hosted Projects — Full Index

**138 projects** · **73 tested & verified** · Updated 2026-08-04

Each project is a ready-to-run `stacker.yml` deployment. See [README.md](../README.md) for quick start.

---

## AI & LLM (3)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| ai-knowledge-base | langgenius/dify-api, qdrant/qdrant | 8080 | postgres, qdrant | |
| ai-automation-workflows | flowiseai/flowise, n8nio/n8n | 3000 | postgres | |
| private-sovereign-ai | ghcr.io/open-webui/open-webui | 3000 | — | |

## Analytics (20)

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

## Automation (11)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| activepieces | ghcr.io/activepieces/activepieces | 8080 | postgres, redis | |
| automatisch | automatisch/automatisch | 3000 | postgres | |
| calcom | calcom/cal.com | 3000 | postgres | |
| changedetection | ghcr.io/dgtlmoon/changedetection.io | 5000 | — | |
| dify | (static) | — | — | |
| homeassistant | lscr.io/linuxserver/homeassistant | 8123 | — | |
| n8n | n8nio/n8n | 5678 | postgres | |
| rallly | lukevella/rallly | 3000 | postgres | |
| typebot | baptistearno/typebot-builder | 3001 | postgres | |
| vikunja | (Dockerfile) | 3456 | postgres | ⚠️ |

## Bookmarks & Link Sharing (5)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| ArchiveBox | archivebox/archivebox | 8000 | — | |
| freshrss | lscr.io/linuxserver/freshrss | 8080 | — | |
| linkding | sissbruecker/linkding | 9090 | — | |
| linkwarden | ghcr.io/linkwarden/linkwarden | 3000 | postgres | ✅ |
| wallabag | wallabag/wallabag | 80 | postgres, redis | |

## CMS & Blogging (8)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| bookstack | lscr.io/linuxserver/bookstack | 6875 | mariadb | |
| directus | directus/directus | 8055 | postgres | |
| ghost | ghost:5-alpine | 2368 | mysql | ✅ |
| outline | outlinewiki/outline | 3000 | postgres, redis | ✅ |
| strapi | naskio/strapi | 1337 | postgres | ✅ |
| wordpress | wordpress | 8080 | mysql | ✅ |
| wordpress-matomo | wordpress | 8080 | mysql, mariadb | |
| writefreely | writeas/writefreely | 8080 | mysql | ⚠️ |

## Communication (11)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| AstrBot | soulter/astrbot | 6185 | — | |
| chatwoot | chatwoot/chatwoot | 3000 | postgres, redis | |
| discourse | discourse/discourse | 80 | postgres, redis | ✅ |
| gotify | gotify/server | 8080 | — | |
| jitsi | jitsi/web:unstable | 80 | — | ✅ |
| mattermost | mattermost/mattermost-enterprise-edition | 8065 | postgres | |
| rocket-chat | rocket.chat | 3000 | mongo | ✅ |
| screego | ghcr.io/screego/server | 5050 | — | |
| synapse | matrixdotorg/synapse | 8008 | postgres | ✅ |
| listmonk | listmonk/listmonk | 9000 | postgres | ✅ |
| zulip | zulip/docker-zulip | 80 | postgres | |

## Dashboard (5)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| appsmith | appsmith/appsmith-ce | 80 | — | |
| dashy | lissy93/dashy | 8082 | — | ✅ |
| grist | gristlabs/grist | 8484 | — | ⚠️ |
| homer | b4bz/homer | 8080 | — | |
| organizr | organizr/organizr | 9983 | — | |

## Developer & DevOps Tools (15)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| caddy | caddy | 80 | — | |
| cyberchef | ghcr.io/gchq/cyberchef | 8000 | — | ✅ |
| floci | floci/floci | 4566 | — | |
| gitness | harness/gitness | 3000 | — | ✅ |
| gitea | gitea/gitea | 3000 | postgres | ✅ |
| hermes-agent | (Dockerfile) | 8000 | — | |
| insforge | (node) | 7130 | — | |
| it-tools | corentinth/it-tools | 8083 | — | ✅ |
| network-tools | trydirect/network-tools | — | — | |
| nocodb | nocodb/nocodb | 8080 | postgres | ✅ |
| semaphore | semaphoreui/semaphore | 3000 | postgres | ✅ |
| supabase | kong/kong:3.9.1 | 8000 | postgres | ✅ |
| traefik | traefik:v3.0 | 80 | — | |
| wireguard | lscr.io/linuxserver/wireguard | 51820 | — | |
| woodpecker-ci | woodpeckerci/woodpecker-server | 8000 | — | |

## Document Management (8)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| archivesspace | archivesspace/archivesspace | 8080 | mysql, solr | |
| docmost | docmost/docmost | 3000 | postgres, redis | ✅ |
| mail-archiver | s1t5/mailarchiver | 5000 | postgres | |
| openarchiver | logiclabshq/open-archiver | 3000 | postgres, valkey, meilisearch | |
| paperless-ngx | ghcr.io/paperless-ngx/paperless-ngx | 8000 | postgres, redis | ✅ |
| stirling-pdf | frooodle/s-pdf | 8080 | — | |
| outline | outlinewiki/outline | 3000 | postgres, redis | ✅ |
| kopia | kopia/kopia | 51515 | — | |

## File Management (10)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| duplicati | lscr.io/linuxserver/duplicati | 8200 | — | |
| filebrowser | filebrowser/filebrowser | 8080 | — | ✅ |
| minio | minio/minio | 9000 | — | |
| nextcloud | nextcloud | 8080 | mariadb, redis | ✅ |
| pingvin-share | stonith404/pingvin-share | 3000 | — | ✅ |
| rustfs | rustfs/rustfs | 9000 | — | ✅ |
| s4core | s4core/s4core | 9000 | — | ✅ |
| syncthing | lscr.io/linuxserver/syncthing | 8384 | — | |

## Media (17)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| audiobookshelf | ghcr.io/advplyr/audiobookshelf | 13378 | — | |
| bitmagnet | ghcr.io/bitmagnet-io/bitmagnet | 3333 | postgres | |
| calibre-web | linuxserver/calibre-web | 8083 | — | |
| comfyui | ashleykza/comfyui | 8188 | — | |
| frigate | ghcr.io/blakeblackshear/frigate | 5000 | — | |
| ganymede | ghcr.io/zibbp/ganymede | 4800 | postgres | ✅ |
| immich | ghcr.io/immich-app/immich-server | 2283 | postgres, redis | |
| jellyfin | jellyfin/jellyfin | 8096 | — | ✅ |
| jellyseerr | fallenbagel/jellyseerr | 5055 | — | |
| kavita | lscr.io/linuxserver/kavita | 5000 | — | ✅ |
| komga | gotson/komga | 25600 | — | ✅ |
| metube | alexta69/metube | 8081 | — | ✅ |
| navidrome | deluan/navidrome | 4533 | — | ✅ |
| ombi | lscr.io/linuxserver/ombi | 3579 | — | |
| romm | rommapp/romm | 8080 | mariadb | ✅ |
| swarm-ui | (Dockerfile) | 7801 | — | |
| tautulli | lscr.io/linuxserver/tautulli | 8181 | — | ✅ |

## Monitoring (9)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| crowdsec | crowdsecurity/crowdsec | — | — | |
| glances | nicolargo/glances:latest-full | 61208 | — | ✅ |
| goaccess | nginx:1.27-alpine | 8080 | — | |
| grafana | grafana/grafana | 3000 | — | ✅ |
| pihole | pihole/pihole | 8080 | — | ✅ |
| speedtest-tracker | lscr.io/linuxserver/speedtest-tracker | 8080 | — | |
| stackdog | trydirect/stackdog | 5000 | — | |
| uptimekuma | louislam/uptime-kuma:2 | 3001 | — | ✅ |

## Note-taking (3)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| hedgedoc | quay.io/hedgedoc/hedgedoc | 3000 | postgres | ✅ |
| memos | ghcr.io/usememos/memos | 5230 | — | |
| trilium | zadam/trilium | 8081 | — | ✅ |

## Password Management (6)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| bitwarden | vaultwarden/server | 80 | postgres | |
| hanko | ghcr.io/teamhanko/hanko | 8000 | postgres | ⚠️ |
| infisical | infisical/infisical | 8080 | postgres | ✅ |
| keycloak | quay.io/keycloak/keycloak | 8080 | postgres | |
| onetimesecret | onetimesecret/onetimesecret | 3000 | redis | |
| vaultwarden | vaultwarden/server | 8080 | — | ✅ |
| zitadel | ghcr.io/zitadel/zitadel | 8080 | postgres, redis | ✅ |

## Recipe & Lifestyle (3)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| grocy | lscr.io/linuxserver/grocy | 9283 | — | ✅ |
| mealie | ghcr.io/mealie-recipes/mealie | 9925 | — | |
| tandoor | vabene1111/recipes | 8080 | postgres | ✅ |

## Search (1)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| meilisearch | getmeili/meilisearch | 7700 | — | ✅ |

## Self-hosting (2)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| coolify | coollabsio/coolify | 8000 | postgres, redis | |
| portainer | portainer/portainer-ce | 9000 | — | |

## Social (7)

| Project | Image | Port | DB | Tested |
|---------|-------|------|----|:------:|
| discourse | discourse/discourse | 80 | postgres, redis | ✅ |
| lemmy | dessalines/lemmy:0.19.11 | 8536 | postgres | ✅ |
| mastodon | ghcr.io/mastodon/mastodon | 3000 | postgres, redis | ✅ |
| postiz-app | ghcr.io/gitroomhq/postiz-app | 4007 | postgres, redis, elasticsearch | ✅ |
| socioboard | sintelli/socioboard-web | 80 | mysql, mongo | |

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
