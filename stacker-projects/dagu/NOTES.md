# dagu — deploy notes (fixture issue, not a stacker defect)

- **Date:** 2026-08-25
- **Deployment:** #845, server `dagu-efec` (id 598), Hetzner fsn1 (49.12.47.82)

## Result: deploys, but the app crashloops
- `stacker deploy --target cloud --force-new` **completed** — server provisioned,
  compose deployed, `project-app-1` created.
- BUT the container is `Restarting (1)` — dagu crashloops on startup:
  ```
  Error: failed to create Wiki store: … mkdir /var/lib/dagu/dags/wiki: permission denied
  ERROR Failed to create example DAG … open /var/lib/dagu/dags/…: permission denied
  ```
- Result: nothing listens on `:8080` → `curl` returns HTTP 000.

## Root cause (app/fixture, not stacker)
The `dagu_data:/var/lib/dagu` named volume is created **root-owned**, but the
`ghcr.io/dagucloud/dagu:latest` image runs as a **non-root** user, so it cannot
write its DAG directory. This is a per-image volume-ownership mismatch — the
Stacker deploy pipeline worked correctly (server, network, compose, volume all
provisioned); the app just can't use a root-owned volume.

## Fix (needs fixture change — not applied without confirmation)
Options for `dagu/stacker.yml`:
- add `user: "0:0"` (run dagu as root), or
- set `DAGU_HOME`/data dir to a path the image's user owns, or
- add an init step to `chown` the volume.

Not a stacker CLI bug → not filed as a GitHub issue.
