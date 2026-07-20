# From Zero to Pipe Execution: A Deep Dive into Stacker's PIPE System

*How we debugged, reverse-engineered, and got the full pipe trigger flow working end-to-end.*

---

## The Goal

We wanted to build and test the complete PIPE workflow in Stacker: create endpoints manually, activate them remotely, and trigger execution between containers on a live server. The stack:

- **Directus** — headless CMS, source of data
- **Chatwoot** — customer support platform, target for data
- **Stacker** — deployment platform orchestrating both

The promise: a single `stacker pipe trigger` command would fetch data from Directus and push it to Chatwoot. In practice, getting there was a four-day debugging odyssey across three servers, two Docker networks, and a orphaned AMQP consumer.

---

## Day 1: Creating the Pipe

The `stacker pipe create` command needed a `--name` flag — previously, it always prompted interactively, which broke CI and scripting. We added the flag to `src/console/commands/cli/pipe.rs`:

```bash
stacker pipe create directus chatwoot \
  --source-endpoint "POST /items" \
  --target-endpoint "POST /api/v1/conversations" \
  --source-fields "name,email,message" \
  --target-fields "content" \
  --name "directus-chatwoot"
```

This created the pipe template locally. Remote activation worked on the first try — the pipe instance was registered with the Stacker API and linked to our deployment.

**Takeaway:** The pipe creation flow (CLI → API → DB) is solid. The bottleneck was always the execution side.

---

## Day 2: The Agent Mystery

With the pipe created, we tried `stacker pipe trigger`. It hung for 30 seconds, then timed out. No error, no output. The command was clearly reaching the server, but nothing was executing.

### The agent status panel

On the target server (Hetzner, `46.224.127.228`), we had the `statuspanel` container running — the web UI for Stacker's deployment dashboard. But the agent that actually executes commands? It was running in the wrong mode.

The Dockerfile's default entrypoint starts a web server:

```dockerfile
ENTRYPOINT ["/usr/local/bin/status", "serve", "--with-ui"]
```

But for pipe execution, the agent needs to run as a **daemon** — a long-polling background process that pulls commands from the Stacker API and executes them locally. We overrode the entrypoint:

```bash
docker run -d \
  --name statuspanel_agent \
  --entrypoint /usr/local/bin/status \
  -c /app/config.json \
  ...
```

### The deployment hash problem

Even with the correct mode, the agent returned 403 errors. The issue: the agent was registered with an old `deployment_hash`. Every deployment in Stacker gets a unique hash (`deployment_<hex>`), and the agent authenticates using this hash. After redeploying, we needed to re-register the agent with the new hash.

```bash
# Find current deployment hash
curl -s "https://stacker.try.direct/api/v1/project/330/deployments" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0].deployment_hash'
# → "deployment_76669ce5-7105-4303-8630-6060f83efab9"
```

**Lesson:** Every time you redeploy, check if the agent's deployment hash is still valid.

---

## Day 3: Network Isolation

With the agent registered and polling, pipe scan worked — it found the Directus container and returned its endpoints. But pipe trigger still timed out.

### Two networks, one problem

The target server has two Docker networks:

| Network | Purpose |
|---|---|
| `project_app-network` | Bridge network for project containers (Directus, Chatwoot) |
| `default_network` | External network for the status panel agent |

The agent was on `default_network`. The project containers were on `project_app-network`. Docker bridge networks are isolated by default — containers on different networks can't reach each other by IP.

The agent could resolve container names (it lists all running containers), but couldn't actually connect to them. The fix:

```bash
docker network connect project_app-network statuspanel_agent
```

**But wait** — the agent was also on `project_app-network` already. What was actually happening? The `statuspanel` (UI) container was on `default_network`, and the agent daemon was on `project_app-network`. They're two separate containers. The agent needed to be on the project's network.

---

## Day 4: The Execution

With networking and naming fixed, pipe trigger finally executed. The agent received the command, parsed it, and attempted to run:

```
failed to fetch trigger_pipe source: source container request failed with code 127:
/bin/sh: curl: not found
```

The Directus container doesn't have `curl` installed. The agent tries to fetch source data by running `curl` inside the target container via `docker exec`. This is a limitation of the current pipe executor — it assumes `curl` is available.

But the important thing: **the mechanism works**. The command was received, executed, and reported back. The failure is at the application level (missing curl), not the infrastructure level.

---

## What We Discovered

### The orphaned AMQP consumer

While debugging, we found `agent-executor` — a standalone Rust binary that connects to RabbitMQ and listens for `StepCommand` messages. We built it, deployed it, and watched it crash repeatedly. Here's the thing: **no code in Stacker ever publishes `StepCommand` to RabbitMQ**.

The `StepCommand` type exists in `src/models/agent_protocol.rs`, with routing keys and exchange names defined. The binary in `src/bin/agent_executor.rs` consumes from the `pipe_execution` exchange. But there's no publisher. The flow was designed but never wired up.

The actual pipe execution path goes through HTTP long-polling:

```
CLI → Dashboard API → DB command queue → statuspanel_agent polls → executes locally
```

Not through AMQP:

```
(what we expected) CLI → RabbitMQ → agent-executor → execute
```

### Two parallel architectures

Stacker has two execution paths that were never connected:

| Path | Status | Used by |
|---|---|---|
| HTTP long-polling (statuspanel_agent) | Working | `stacker pipe trigger`, `pipe scan` |
| AMQP (agent-executor) | Orphaned, never wired | Nothing |

The AMQP path was built as infrastructure but the Stacker API never publishes to it. The HTTP path works end-to-end but has limitations (assumes curl in containers).

---

## The Working Flow

Here's the complete flow that actually works today:

```
1. Create pipe (CLI)
   stacker pipe create directus chatwoot --source-endpoint ... --name "directus-chatwoot"
   → Creates pipe template + instance in Stacker DB

2. Activate pipe (CLI)
   stacker pipe activate --server 46.224.127.228 --pipe <PIPE_ID>
   → Enqueues activation command to agent

3. Scan endpoints (CLI)
   stacker pipe scan directus --server 46.224.127.228
   → Agent runs probe on Directus container
   → Returns available endpoints

4. Trigger execution (CLI)
   stacker pipe trigger directus --server 46.224.127.228 --pipe "directus-chatwoot"
   → Agent receives command via long-poll
   → Executes curl inside Directus container
   → Pushes data to Chatwoot
   → Reports result back to API
```

---

## Lessons Learned

### 1. Docker networking is the #1 gotcha

Every cross-container communication issue we hit was network-related. The agent must be on the same Docker network as the containers it manages. This is not obvious from the Stacker documentation.

### 2. Deployment hashes are ephemeral

Every deploy creates a new hash. If the agent is registered with an old hash, all commands fail with 403. After any deploy, re-register the agent.

### 3. Daemon mode is not the default

The Dockerfile entrypoint starts a web server. For pipe execution, you need the daemon. This is a configuration detail that's easy to miss.

### 4. AMQP was designed but never connected

The `agent-executor` binary and RabbitMQ integration exist in the codebase, but no code publishes to the `pipe_execution` exchange. The HTTP long-polling path is the only one that works.

---

## What's Next

1. **Install curl in target containers** — or modify the pipe executor to use a different HTTP client
2. **Wire up the AMQP path** — publish `StepCommand` from the Stacker API when pipes are triggered
3. **Document the two execution paths** — clarify which one is active and when

---

## Files Referenced

- `src/console/commands/cli/pipe.rs` — pipe create/trigger commands
- `src/models/agent_protocol.rs` — `StepCommand`, `StepResultMsg` (AMQP types)
- `src/bin/agent_executor.rs` — orphaned AMQP consumer
- `statuspanel_agent` daemon — `trydirect/status:pipe-agent-fixes`
- `docs/pipe-howto.md` — updated pipe documentation

---

*Published July 2026. Tested on Stacker CLI dev branch, target server Hetzner cpx22 (2 vCPU, 2GB RAM), status panel image `trydirect/status:pipe-agent-fixes`.*
