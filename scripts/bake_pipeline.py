"""Bake mode for scripts/test-templates.py.

After a template is deployed and verified, instead of `stacker destroy`:

  1. read the deployment lock (deployment id, build box IP, SSH key);
  2. record the build box's generated values and SSH host key;
  3. POST /api/admin/bake on the stacker API and poll it until done;
  4. smoke clone: POST /api/v1/deploy/clone, wait until the clone is healthy;
  5. check every `generated` value and the SSH host key differ on the clone;
  6. append one row to BAKES.md, with the servers to remove.

Nothing here deletes a server. The build box and the clone are listed in
BAKES.md and removed by hand (BAKE_PIPELINE_PLAN.md, decision 1).

Needs PyYAML: uv run --with pyyaml python3 scripts/test-templates.py --bake ...
API access: STACKER_URL (default https://try.direct/stacker) and STACKER_TOKEN,
or the token the stacker CLI stored at `stacker login`. Baking needs an admin
account; the smoke clone needs a plan that can clone.
"""

import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:  # only --bake needs it; the plain test run does not
    yaml = None

DEFAULT_STACKER_URL = "https://try.direct/stacker"
BAKES_HEADER = (
    "# Bakes\n\n"
    "One row per `test-templates.py --bake` run. **Servers to remove** are left\n"
    "running on purpose: nothing in the pipeline deletes servers.\n\n"
    "| Date | Stack | Version | image_id | Smoke clone | Servers to remove |\n"
    "|---|---|---|---|---|---|\n"
)


def _yaml():
    if yaml is None:
        raise RuntimeError("--bake needs PyYAML: uv run --with pyyaml python3 scripts/test-templates.py ...")
    return yaml


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------
def generated_keys(stacker_yml_text):
    """Fields the contract regenerates per install: `mutability: generated` and
    the legacy `secret:` lists."""
    doc = _yaml().safe_load(stacker_yml_text) or {}
    services = ((doc.get("config_contract") or {}).get("services")) or {}
    keys = set()
    for target in services.values():
        target = target or {}
        for name, policy in (target.get("fields") or {}).items():
            if isinstance(policy, dict) and policy.get("mutability") == "generated":
                keys.add(name)
        keys.update(target.get("secret") or [])
    return keys


def _published_port(mapping):
    """Host port of a compose-style mapping, None when bound to loopback."""
    parts = str(mapping).split("/")[0].split(":")
    if len(parts) == 3:
        return None if parts[0] in ("127.0.0.1", "localhost", "::1") else parts[1]
    if len(parts) == 2:
        return parts[0]
    return parts[0] or None


def health_url(server_ip, stacker_yml_text):
    """The app's first public port plus `monitoring.healthcheck.endpoint`."""
    doc = _yaml().safe_load(stacker_yml_text) or {}
    ports = ((doc.get("app") or {}).get("ports")) or []
    port = next((p for p in map(_published_port, ports) if p), None)
    endpoint = (((doc.get("monitoring") or {}).get("healthcheck")) or {}).get("endpoint") or "/"
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    host = f"{server_ip}:{port}" if port and port != "80" else server_ip
    return f"http://{host}{endpoint}"


def parse_lock(text):
    """The CLI deployment lock (.stacker/deployment-cloud.lock, YAML)."""
    lock = _yaml().safe_load(text) or {}
    if not lock.get("deployment_id") or not lock.get("server_ip"):
        raise ValueError("the deployment lock has no deployment_id or server_ip")
    return lock


def parse_env(text):
    env = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, sep, value = line.partition("=")
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key.strip()):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        env[key.strip()] = value
    return env


def values_not_reset(build_env, clone_env, keys):
    """Generated keys whose clone value is empty or equal to the build box's."""
    if keys and not any(key in build_env for key in keys):
        return ["none of the generated keys found on the build box"]
    problems = []
    for key in sorted(keys):
        if key not in build_env:
            continue  # not used by this stack's env
        clone_value = clone_env.get(key, "")
        if clone_value == "":
            problems.append(f"{key} (empty on the clone)")
        elif clone_value == build_env[key]:
            problems.append(f"{key} (same value)")
    return problems


def bakes_row(stack, version, image_id, smoke, servers, date=None):
    date = date or datetime.now().strftime("%Y-%m-%d")
    return f"| {date} | {stack} | {version} | {image_id} | {smoke} | {'; '.join(servers)} |"


def append_bakes_row(bakes_file, row):
    path = Path(bakes_file)
    if not path.exists():
        path.write_text(BAKES_HEADER)
    with open(path, "a") as f:
        f.write(row + "\n")


# ---------------------------------------------------------------------------
# Stacker API
# ---------------------------------------------------------------------------
def _cli_credentials():
    for path in (
        Path.home() / "Library" / "Application Support" / "stacker" / "credentials.json",
        Path.home() / ".config" / "stacker" / "credentials.json",
    ):
        if path.exists():
            return json.loads(path.read_text())
    return {}


def api_settings():
    creds = _cli_credentials()
    token = os.environ.get("STACKER_TOKEN") or creds.get("access_token")
    url = os.environ.get("STACKER_URL") or creds.get("server_url") or DEFAULT_STACKER_URL
    if not token:
        raise RuntimeError("no API token: set STACKER_TOKEN or run `stacker login`")
    return url.rstrip("/"), token


def api(method, path, body=None, timeout=60):
    base, token = api_settings()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{base}{path}",
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as err:
        try:
            payload = json.loads(err.read() or b"null")
        except ValueError:
            payload = None
        return err.code, payload


# ---------------------------------------------------------------------------
# Servers (read-only: SSH reads and HTTP checks)
# ---------------------------------------------------------------------------
def ssh(ip, key_path, command, user="root", port=22, timeout=60):
    cmd = [
        "ssh", "-i", str(key_path), "-p", str(port),
        "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
        "-o", f"UserKnownHostsFile={tempfile.gettempdir()}/bake_known_hosts",
        "-o", "ConnectTimeout=15",
        f"{user}@{ip}", command,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"ssh {ip} `{command}` exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout


def host_key(ip):
    result = subprocess.run(
        ["ssh-keyscan", "-t", "ed25519", "-T", "10", ip], capture_output=True, text=True, timeout=30
    )
    keys = [line.split(None, 1)[1] for line in result.stdout.splitlines() if line and not line.startswith("#")]
    return keys[0] if keys else None


def build_box_env(lock):
    """The stack's .env on the build box, read before it is sanitized."""
    ls = json.loads(ssh(lock["server_ip"], lock["ssh_key"], "docker compose ls --all --format json",
                        user=lock.get("ssh_user") or "root", port=lock.get("ssh_port") or 22))
    dirs = sorted({
        p["ConfigFiles"].split(",")[0].rsplit("/", 1)[0]
        for p in ls
        if "/statuspanel/" not in p["ConfigFiles"] and "/nginx_proxy_manager/" not in p["ConfigFiles"]
    })
    if len(dirs) != 1:
        raise RuntimeError(f"expected one stack directory on the build box, found {dirs}")
    return parse_env(ssh(lock["server_ip"], lock["ssh_key"], f"cat {dirs[0]}/.env 2>/dev/null || true",
                         user=lock.get("ssh_user") or "root", port=lock.get("ssh_port") or 22))


def wait_http(url, timeout=900):
    deadline = time.time() + timeout
    last = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                if 200 <= resp.status < 400:
                    return True, f"{url} -> {resp.status}"
                last = f"{url} -> {resp.status}"
        except Exception as err:  # noqa: BLE001 - any failure means "not yet"
            last = f"{url}: {err}"
        time.sleep(15)
    return False, last


# ---------------------------------------------------------------------------
# The bake
# ---------------------------------------------------------------------------
def bake(template, work_dir, bakes_file, log=print):
    """Bake the deployed build box in `work_dir`, smoke-clone it, record it.
    Returns True when the bake and the smoke clone both passed."""
    stacker_yml = (Path(work_dir) / "stacker.yml").read_text()
    lock = parse_lock((Path(work_dir) / ".stacker" / "deployment-cloud.lock").read_text())
    ip = lock["server_ip"]
    servers = [f"build box {lock.get('server_name') or '?'} {ip}"]
    keys = generated_keys(stacker_yml)

    log(f"  [bake 1/5] Recording the build box ({len(keys)} generated keys)...")
    build_env = build_box_env(lock)
    build_host_key = host_key(ip)

    log("  [bake 2/5] POST /api/admin/bake ...")
    status, resp = api("POST", "/api/admin/bake", {
        "deployment_id": lock["deployment_id"],
        "stack": template,
        "health_url": health_url(ip, stacker_yml),
    })
    if status != 202:
        append_bakes_row(bakes_file, bakes_row(template, "-", "-", f"bake refused {status}: {resp}", servers))
        log(f"  FAIL: bake refused ({status}): {resp}")
        return False
    job = resp["item"]
    version = job["version"]

    log(f"  [bake 3/5] Waiting for bake {job['id']} ...")
    deadline = time.time() + 45 * 60
    while job["status"] == "running" and time.time() < deadline:
        time.sleep(20)
        _, resp = api("GET", f"/api/admin/bake/{job['id']}")
        job = (resp or {}).get("item") or job
    if job["status"] != "done":
        append_bakes_row(bakes_file, bakes_row(template, version, "-", f"bake {job['status']}: {job.get('error')}", servers))
        log(f"  FAIL: bake {job['status']}: {job.get('error')}")
        return False
    image_id = job["image_id"]

    log(f"  [bake 4/5] Smoke clone of image {image_id} ...")
    status, clone = api("POST", "/api/v1/deploy/clone", {
        "stack": template,
        "version": version,
        "domain": f"{template}-smoke.try.direct",
    }, timeout=300)
    if status != 200:
        append_bakes_row(bakes_file, bakes_row(template, version, image_id, f"clone refused {status}: {clone}", servers))
        log(f"  FAIL: clone refused ({status}): {clone}")
        return False
    clone_ip = clone.get("public_ipv4")
    servers.append(f"clone {clone.get('server_id')} {clone_ip}")

    problems = []
    healthy, detail = wait_http(health_url(clone_ip, stacker_yml))
    if not healthy:
        problems.append(f"not healthy: {detail}")
    else:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".pem") as f:
            f.write(clone["ssh_private_key"])
            clone_key = f.name
        os.chmod(clone_key, 0o600)
        try:
            clone_env = parse_env(ssh(clone_ip, clone_key, "cat /etc/stacker/env"))
        finally:
            os.unlink(clone_key)
        problems += values_not_reset(build_env, clone_env, keys)
        clone_host_key = host_key(clone_ip)
        if build_host_key and clone_host_key == build_host_key:
            problems.append("SSH host key same as the build box")

    log("  [bake 5/5] Recording in BAKES.md ...")
    smoke = "ok" if not problems else "FAIL: " + ", ".join(problems)
    append_bakes_row(bakes_file, bakes_row(template, version, image_id, smoke, servers))
    log(f"  {'OK' if not problems else 'FAIL'}: {smoke}")
    log("  Servers to remove by hand: " + "; ".join(servers))
    return not problems
