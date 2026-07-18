# Building a WordPress → Matomo Pipe with Stacker

I spent a session trying to connect two apps on the same server with Stacker
PIPE — and hit every wall you can imagine. Here's the full story, the fixes,
and where the gaps are.

## What I wanted

When a visitor submits a contact form on a WordPress site, send a custom event
to Matomo analytics — all running on the same server. No third-party services,
no custom code.

```
WordPress form → Stacker PIPE → Matomo tracking event
```

## Step 1: Deploy both apps

I created a combined project `wordpress-matomo` with all four containers:

| Container | Image | Purpose |
|-----------|-------|---------|
| wordpress-matomo | wordpress | Blog with contact form |
| wp-db | mysql:8.0 | WordPress database |
| matomo | matomo:latest | Analytics |
| matomo-db | mariadb:11 | Matomo database |

One `stacker deploy` put everything on a Hetzner cloud server. Worked
flawlessly on the first try.

## Step 2: The form

I installed Contact Form 7 on WordPress and created a simple form with name,
email, and message fields. Then I also added a plain HTML form directly on the
homepage to make sure the agent could find it.

```bash
curl -s http://<your-server-ip>:8080/ | grep '<form'
```

Confirmed: one `<form>` element with action `/wp-json/demo/v1/submit`.

## Step 3: The agent scan — first wall

```bash
stacker pipe scan --app wordpress-matomo
```

**Result:** empty. No endpoints, no forms, no protocols detected.

The agent connected to the container but returned nothing. The container was
running, the form was serving, but the agent couldn't find it.

### Why?

I checked the agent logs on the server:

```
WARN No matching container found. Attempted patterns: exact match, prefix, suffix, contains
app_code="wordpress-matomo"
available_containers=["project-app-1", "project-matomo-1", ...]
```

The agent resolves containers by **name**, not by the `my.stacker.service`
label. Stacker generates the main app compose service with the hardcoded name
`app`, producing containers named `project-app-1`. The agent's app code is
`wordpress-matomo` but the container name `project-app-1` doesn't match.

### The fix

I edited the generated compose to rename the service:

```bash
sed -i 's/^  app:/  wordpress-matomo:/' .stacker/docker-compose.yml
sed -i 's/my.stacker.service: "app"/my.stacker.service: "wordpress-matomo"/' .stacker/docker-compose.yml
```

After redeploy, the agent log showed:

```
INFO Container name resolved via compose service label
app_code="wordpress-matomo" resolved_name="project-wordpress-matomo-1"
```

## Step 4: Network isolation — second wall

Even with the container name resolved, the probe returned empty. The agent
could see the container but couldn't reach it.

```bash
docker inspect statuspanel_agent | jq '.[].NetworkSettings.Networks | keys'
```

**Result:** the agent is on `default_network`, project containers on
`project_app-network`. Two isolated Docker bridge networks.

Docker bridge networks are isolated from each other — containers on different
networks can't communicate directly. The agent resolves the name but can't
open a TCP connection.

### The fix

```bash
docker network connect project_app-network statuspanel_agent
```

After this, the agent connects to the container and the scan returns real data:

```json
{
  "forms": [{
    "action": "/contact#wpcf7-f5-p6-o1",
    "fields": ["your-name", "your-email", "your-subject", "your-message"]
  }]
}
```

The `--container` flag also forces the `direct_container` probe scope, which
finds forms and REST endpoints when the `remote_app` scope does not.

## Step 5: Probe scope — third wall

Even with the network connected and container reachable, the `remote_app`
probe scope (used by `stacker pipe create`) returns empty. The
`direct_container` scope (used by `--container`) finds everything.

| Scope | Trigger | Form discovery |
|-------|---------|----------------|
| `remote_app` | `--app <CODE>` (no `--container`) | ❌ empty |
| `direct_container` | `--app <CODE> --container <NAME>` | ✅ detected |

This is because `remote_app` probes the app's published host port, while
`direct_container` connects directly to the container's internal IP. The
probe behaviors are different.

## Key findings

**Container matching:** The agent matches app codes to container names using
string patterns (exact/prefix/suffix/contains). Renaming the compose service
from `app` to the project name fixes the match, but this is a workaround.
The root fix belongs in `src/cli/generator/compose.rs:189`.

**Network injection:** The status-panel agent runs on an external network.
Project containers run on a compose-scoped bridge. They can't communicate
unless manually bridged. Stacker already has `inject_external_network()` in
`compose_service_sync.rs` — it's used for NPM proxy mode but not for
status-panel mode. This is the systemic fix.

**Probe scope gap:** `remote_app` and `direct_container` probes behave
differently. The `pipe create` wizard uses `remote_app` which doesn't find
forms that `direct_container` does. The agent's probe protocol handler needs
alignment.

## Commands cheat sheet

```bash
# Check agent sees containers
stacker agent status

# Scan with direct container probe (works)
stacker pipe scan --app <APP> --container <NAME> --protocols html_forms

# Check agent logs on server
docker logs statuspanel_agent | grep -i 'probe\|match\|resolve'

# Check which networks the agent is on
docker inspect statuspanel_agent --format '{{range $k,$_ := .NetworkSettings.Networks}}{{$k}} {{end}}'

# Bridge the networks
docker network connect project_app-network statuspanel_agent

# Rename compose service (workaround)
sed -i 's/^  app:/  <project-name>:/' .stacker/docker-compose.yml
sed -i 's/my.stacker.service: "app"/my.stacker.service: "<project-name>"/' .stacker/docker-compose.yml

# Check container labels
docker inspect <container> --format '{{range $k,$v := .Config.Labels}}{{$k}}={{$v}}{{"\n"}}{{end}}'

# Create a simple form page in WordPress
wp post create --post_type=page --post_title=Home --post_status=publish \
  --post_content='<form id=test action=/ method=POST><input type=text name=email><button>Submit</button></form>'
wp option update show_on_front page
wp option update page_on_front <PAGE_ID>
```

## What's next

Three paths forward, from quickest to most thorough:

1. **One-liner workaround** (this session): `docker network connect` + compose
   service rename. Works today, lost on agent restart.

2. **Compose edit** (per-project): Add `default_network` as an external network
   in the project's compose, so agent + project share a network. Survives
   redeploy.

3. **Stacker source fix** (systemic): Mirror the NPM proxy network injection
   for the status-panel path in `deploy.rs` + `compose_service_sync.rs`. Makes
   every agent-mode deployment reachable with zero project changes.

The PIPE system is architecturally sound — the CLI, API, agent communication,
and execution engine all work. The gaps are in container name resolution and
network bridging, both straightforward to fix.
