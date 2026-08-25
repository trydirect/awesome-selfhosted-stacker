# Security Policy

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Report vulnerabilities privately to the maintainers via email:

**security@try.direct**

Please include:

- The affected project (`stacker-projects/<name>`) and file (`stacker.yml`,
  `generate-secrets.sh`, `.env.example`, etc.)
- The vulnerability type (e.g., exposed secret, injection, privilege
  escalation, insecure default) and severity
- Steps to reproduce, including any relevant logs
- A suggested fix, if you have one

You should receive an acknowledgment within **48 hours**. We aim to ship a fix
and coordinate disclosure within **90 days** of confirmation.

## Supported Versions

This repository is a collection of deployment templates for the Stacker
platform. Each `stacker-projects/<name>/` directory is an independent, mostly
composable deployment and is treated as a fixture for testing the Stacker CLI.

We provide security support for:

| Scope | Supported |
|-------|-----------|
| `stacker.yml` templates in this repo | ✅ |
| `.env.example` / `generate-secrets.sh` in this repo | ✅ |
| Third-party images referenced by templates | ❌ (see below) |
| The Stacker CLI / platform itself | ✅ via [trydirect/stacker](https://github.com/trydirect/stacker) |

## What This Repo Is

This repo ships **deployment configuration**, not application code. It
references official upstream images (e.g., `nextcloud`, `grafana`, `postgres`).
Vulnerabilities in the upstream software itself must be reported to the
upstream project, not here.

## Security Best Practices for Deployments

Every template in this repo follows the "secure project" pattern:

```
project/
  .env.example           # Template with empty secrets — COMMITTED
  .env                   # Actual secrets — GITIGNORED, never commit
  .gitignore             # Protects .env and .stacker/
  scripts/
    generate-secrets.sh  # Idempotent — fills empty keys with openssl rand
  stacker.yml            # Main config
```

### Hard rules

- **Never commit** `.env`, `.env.local`, `.stacker/`, or any generated
  secrets file (e.g., `config.yaml` produced from a template). If a secret
  leaks, rotate it immediately and replace the value.
- **Never hardcode credentials** in `stacker.yml`. Reference them with
  `${VAR}` and let `generate-secrets.sh` fill them from `.env`.
- **Do not reuse real secrets in `.env.example`** — it is public.
- **Cloud deploys:** keep `public_ports` limited to the ports you actually
  need. Without `public_ports`, only SSH (22) is open; opening extra ports
  widens your attack surface.
- **Bind database ports to localhost** when the DB is only used internally:
  `"127.0.0.1:5432:5432"` — never expose a database to the public internet.
- **Use non-default admin credentials** and change the default ports of the
  admin panels where the template allows it.
- **Enable SSL/TLS** and set up database backups before going to production.

### Secret generation

Run the per-project secret generator before deploying:

```bash
cd stacker-projects/<name>
./scripts/generate-secrets.sh
```

The generator only fills keys that are **empty** — it never overwrites an
existing value, so it is safe to re-run.

## Known Security-Relevant Gotchas

- Some templates pin image tags; **avoid un-pinned `:latest`** where a
  specific tag exists (see the "Known image issues" table in `README.md`).
- Bind-mount config files are resolved relative to the compose location on the
  remote host. Prefer baking config files into a custom Dockerfile over bind
  mounts when the file contains secrets.
- Secrets set through `stacker secrets` are stored per scope/service; treat
  them like any other secret material and rotate on compromise.

## Responsible Disclosure Process

1. Reporter sends details to **security@try.direct**.
2. Maintainers acknowledge within 48 hours and triage severity.
3. A fix is prepared and, where feasible, released within 90 days.
4. The vulnerability is disclosed publicly after the fix ships and users have
   had time to update.

## Scope Exclusions

The following are **not** covered by this policy:

- The upstream applications, images, and libraries referenced by templates
  (report to their respective projects).
- The Stacker platform/CLI internals (report via
  [trydirect/stacker](https://github.com/trydirect/stacker)).
- Known limitations of the template test harness documented in `BUGS.md`.

## License

Security patches and disclosures follow the license of this repository.