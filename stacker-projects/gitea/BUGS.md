# gitea — Stacker QA Bugs

## Local deploy fails due to host PostgreSQL port conflict

**[BUG] `stacker deploy --target local` fails because `127.0.0.1:5432` is already allocated**

Steps to reproduce:
1. `cd stacker-projects/gitea`
2. Populate `.env` with `DB_PASSWORD`, `SECRET_KEY`, `INTERNAL_TOKEN`.
3. `source .env`
4. `stacker deploy --target local --force-rebuild --watch`

Expected behaviour:
- Stacker starts the local gitea stack.

Actual behaviour:
- Images pull successfully.
- Container creation fails with:
  ```
  Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint stacker-gitea_db-1 (...): Bind for 127.0.0.1:5432 failed: port is already allocated
  ```
- Exit code 1.

Logs / Evidence:
- Another local stack already binds `127.0.0.1:5432`.

## Cloud deploy pauses with `local-exec provisioner error` and SSH becomes unreachable

**[BUG] `stacker deploy --target cloud` provisions a Hetzner server but pauses during app deploy; port 22 is unreachable and the SSH backup key is never installed**

Steps to reproduce:
1. `cd stacker-projects/gitea`
2. `source .env`
3. `stacker deploy --target cloud --key htz-0 --force-new --watch`

Expected behaviour:
- Server is provisioned, Docker/setup completes, Gitea containers start, and HTTP port 3000 is reachable.

Actual behaviour:
- Server setup reaches `Copy files is done`.
- Deployment pauses with:
  ```
  Deployment has been paused due to internal error. Details: Application Stack: gitea
  Error: local-exec provisioner error
  ```
- SSH to `root@<server_ip>:22` times out.
- `curl http://<server_ip>:3000/` times out.
- Stackers reports:
  ```
  App deploy succeeded, but local SSH backup access was not installed.
  Reason: Deployment to cloud failed: Failed to authorize SSH public key for server ... Connection timed out after 4 seconds
  ```
- Reproduced on a second `force-new` deploy with the same error.

Logs / Evidence:
- Deployment #322 and #323 both paused at the same step.
- `nc -vz <ip> 22` times out; port 3000 is also closed.
