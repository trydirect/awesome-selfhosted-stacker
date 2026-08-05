# AGENTS.md

Generic entry point for AI coding agents (Claude, Copilot, Cursor, Aider, etc.)
working in this repository. Tool-specific files (`CLAUDE.md`,
`copilot-instructions.md`) point back here or duplicate this guidance —
treat this as the source of truth if they ever diverge.

## What this repo is

`awesome-selfhosted-stacker` is a curated collection of 135+ self-hostable apps,
each deployable with a single `stacker.yml` via the **Stacker CLI**
(https://github.com/trydirect/stacker). Every subdirectory under
`stacker-projects/` is an independent, ready-to-run deployment (analytics,
CMS, chat, password managers, AI tools, etc.) sharing the same layout and
commands.

Pipeline: `stacker.yml` → CLI → Stacker API → MQ → Install Service
(Terraform + Ansible) → Cloud Server (Hetzner by default) or local Docker.

## Read these first, in order

1. **`SKILL.md`** (repo root) — the primary knowledge base for this repo.
   Documents the Stacker deploy pipeline in depth: `public_ports`,
   `dockerhub_tag`, cloud deploy requirements, database initialisation, the
   "secure project" pattern, `install.inputs` template variables,
   `command`/`healthcheck` support, known project-specific issues, the
   config bundle/bind-mount pipeline, port conflict validation, a
   deployment verification checklist, common failure patterns, the Rust
   config pipeline source map, testing, the full deploy command reference,
   hooks execution/safety, Vault-backed vs `.env` secrets, and the status
   panel agent. **Always consult `SKILL.md` before debugging a deploy
   failure or explaining stacker behavior** — most edge cases are already
   documented there with root cause and fix.
2. **`README.md`** (repo root) — quick start, deploy targets (local/server/
   cloud), PIPE (connecting apps together), remote monitoring, secret
   management, common commands, customization, security checklist,
   troubleshooting, and the full project catalog.
3. **`copilot-instructions.md`** — the QA/testing agent brief. Defines the
   mission (deploy every project under `stacker-projects/` locally, to a
   fresh cloud server, and to an existing server), environment setup
   (`.env` sourcing), rules (rely on stacker CLI first, ask before
   modifying project files), and reporting format for `BUGS.md` and
   `*_DEPLOY_SUCCESS.md` files.
4. **`HOWTO.md`** / **`BUGS.md`** (repo root) — auto-generated rollups of
   template test successes/failures from `scripts/test-templates.py`. Each
   project directory under `stacker-projects/<name>/` also has its own
   local `BUGS.md` and `*_DEPLOY_SUCCESS.md` files — check those first when
   working on a specific project.

## Repo layout

```
stacker.yml                  # example/template stacker.yml at repo root
SKILL.md                     # Stacker pipeline knowledge base (read first)
README.md                    # user-facing docs, catalog, quick start
copilot-instructions.md      # QA agent brief for testing stacker itself
CLAUDE.md                    # Claude-specific pointer to this file
HOWTO.md / BUGS.md           # aggregated test results (generated)
.env / .env.example          # credentials & host config (gitignored, never commit)
scripts/
  test-templates.py          # drives bulk deploy testing across all projects
  templates.txt              # list of templates under test
docs/                        # deep-dive notes (pipe setup, install fixes, etc.)
stacker-projects/<name>/     # one independent project per subdirectory, each with
                              #   its own stacker.yml, scripts/, and local
                              #   BUGS.md / *_DEPLOY_SUCCESS.md
```

## Working conventions in this repo

- **Never modify files inside a `stacker-projects/<name>/` directory**
  (`stacker.yml`, Dockerfile, app source, etc.) without explicit user
  confirmation first — these are treated as fixtures for testing the
  stacker CLI itself. Exceptions: `BUGS.md` and `*_DEPLOY_SUCCESS.md` test
  artifacts may be created/updated freely.
- **Prefer the `stacker` CLI** for deployment, logs (`stacker logs`), keys
  (`stacker key`), secrets (`stacker secret`), and proxy/ingress. Only fall
  back to `curl`/`ssh`/`docker` when stacker has no equivalent command —
  and note the gap as a potential missing feature in `BUGS.md`.
- **Secrets** live in `.env` (gitignored) and are generated per-project via
  `./scripts/generate-secrets.sh`. Never hardcode credentials or commit
  `.env`.
- Every bug found while exercising stacker should be logged in `BUGS.md`
  (root or project-level) using the `[BUG] Short title` format with steps
  to reproduce, expected vs. actual behavior, and logs/evidence.
- Every successful deployment should produce a `LOCAL_DEPLOY_SUCCESS.md`,
  `CLOUD_DEPLOY_SUCCESS.md`, or `EXISTING_DEPLOY_SUCCESS.md` in the
  project directory, documenting the exact commands used and verification
  steps performed.

## Quick commands

```bash
cd stacker-projects/<name>
./scripts/generate-secrets.sh          # create .env from .env.example
stacker deploy                         # deploy locally
stacker deploy --target cloud --force-rebuild   # deploy to Hetzner cloud
```
