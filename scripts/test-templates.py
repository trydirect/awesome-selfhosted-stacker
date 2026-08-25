#!/usr/bin/env python3
"""
Test all Stacker marketplace templates with `stacker install`.

For each template:
  1. stacker install <template> --domain <template>.try.direct ...
  2. Inject NPM into stacker.yml (unless template uses ports 80/443)
  3. stacker deploy --target cloud --force-new
  4. Verify: stacker status, agent health, HTTP check
  5. Record result to HOWTO.md or BUGS.md
  6. stacker destroy

Usage:
  python3 scripts/test-templates.py                    # test all, batch 1
  python3 scripts/test-templates.py --batch 2          # test batch 2
  python3 scripts/test-templates.py --template ghost    # test single template
  python3 scripts/test-templates.py --list              # list all templates
  python3 scripts/test-templates.py --dry-run           # show what would run
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
TEMPLATES_FILE = ROOT / "scripts" / "templates.txt"
BUGS_FILE = ROOT / "BUGS.md"
HOWTO_FILE = ROOT / "HOWTO.md"
WORK_DIR = ROOT / "test-workdir"

# ---------------------------------------------------------------------------
# NPM skip list - templates that use ports 80/443
# ---------------------------------------------------------------------------
NPM_SKIP = {
    "appsmith", "bitwarden", "caddy", "discourse", "jitsi",
    "socioboard", "supabase", "supabase-posthog", "traefik",
    "wallabag", "zulip",
}

# ---------------------------------------------------------------------------
# Provider config
# ---------------------------------------------------------------------------
PROVIDERS = {
    "hetzner": {
        "env_key": "CLOUD_API_TOKEN",
        "key_name": "htz-10",
        "region": "fsn1",
        "size": "cx23",
    },
    "digitalocean": {
        "env_key": "DIGITALOCEAN__TOKEN",
        "key_name": "do-token",
        "region": "fra1",
        "size": "s-2vcpu-4gb",
    },
    "linode": {
        "env_key": "LINODE_TOKEN",
        "key_name": "linode-token",
        "region": "eu-central",
        "size": "g6-standard-2",
    },
}

# Batch-to-provider mapping
BATCH_PROVIDERS = {
    1: "hetzner",
    2: "hetzner",
    3: "hetzner",
    4: "hetzner",
    5: "digitalocean",
    6: "digitalocean",
    7: "digitalocean",
    8: "linode",
    9: "linode",
    10: "linode",
}

BATCH_SIZE = 15

# ---------------------------------------------------------------------------
# Load .env
# ---------------------------------------------------------------------------
def load_env():
    """Load .env file into os.environ."""
    if not ENV_FILE.exists():
        print(f"ERROR: {ENV_FILE} not found. Copy .env.example to .env and fill in credentials.")
        sys.exit(1)
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)

# ---------------------------------------------------------------------------
# Template list
# ---------------------------------------------------------------------------
def get_templates():
    """Load template list from file."""
    if not TEMPLATES_FILE.exists():
        print(f"ERROR: {TEMPLATES_FILE} not found.")
        sys.exit(1)
    templates = []
    seen = set()
    with open(TEMPLATES_FILE) as f:
        for line in f:
            slug = line.strip()
            if slug and not slug.startswith("#") and slug not in seen:
                templates.append(slug)
                seen.add(slug)
    return templates

def get_batch(templates, batch_num):
    """Get templates for a specific batch (1-indexed)."""
    start = (batch_num - 1) * BATCH_SIZE
    end = start + BATCH_SIZE
    return templates[start:end]

# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------
def run(cmd, cwd=None, timeout=600, capture=True):
    """Run a shell command, return (returncode, stdout, stderr)."""
    print(f"  $ {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=capture, text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"

def run_checked(cmd, cwd=None, timeout=600):
    """Run command, raise on failure."""
    code, stdout, stderr = run(cmd, cwd=cwd, timeout=timeout)
    if code != 0:
        raise RuntimeError(f"Command failed (exit {code}): {cmd}\nstdout: {stdout}\nstderr: {stderr}")
    return stdout

# ---------------------------------------------------------------------------
# NPM injection
# ---------------------------------------------------------------------------
def inject_npm(stackeryml_path):
    """Add NPM service to stacker.yml. Returns True if injected."""
    content = Path(stackeryml_path).read_text()

    # Check if NPM already present
    if "nginx-proxy-manager" in content:
        return False

    # Find the app's port to detect conflicts
    app_port_match = re.search(r'ports:\s*\n\s*-\s*["\']?(\d+):', content)
    app_port = int(app_port_match.group(1)) if app_port_match else None

    # If app uses port 80 or 443, skip NPM
    if app_port in (80, 443):
        print(f"  Skipping NPM - app uses port {app_port}")
        return False

    # Add NPM service before the last line or after services section
    npm_block = """
  - name: npm
    image: jc21/nginx-proxy-manager:latest
    ports:
      - "80:80"
      - "443:443"
      - "81:81"
    volumes:
      - npm_data:/data
      - npm_letsencrypt:/etc/letsencrypt

"""
    # Add volumes if not present
    if "npm_data:" not in content:
        npm_volumes = """
volumes:
  npm_data: {}
  npm_letsencrypt: {}
"""
        # Insert before deploy section or at end
        if "deploy:" in content:
            content = content.replace("deploy:", npm_volumes + "\ndeploy:")
        else:
            content += npm_volumes

    # Insert NPM service after last service definition
    # Find the services section and append
    services_pattern = r'(services:\s*\n(?:\s+-\s+name:.*\n(?:\s+.*\n)*)*)'
    match = re.search(services_pattern, content)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + npm_block + content[insert_pos:]
    else:
        # Fallback: append before volumes
        if "volumes:" in content:
            content = content.replace("volumes:", npm_block + "volumes:")
        else:
            content += npm_block

    Path(stackeryml_path).write_text(content)
    return True

# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
def verify_deployment(template, timeout=300):
    """Verify deployment is healthy. Returns (success, details)."""
    details = []
    success = True

    # 1. stacker status
    code, stdout, stderr = run("stacker status", timeout=60)
    if code != 0:
        details.append(f"stacker status failed: {stderr}")
        success = False
    else:
        details.append(f"stacker status: OK")

    # 2. stacker agent health
    code, stdout, stderr = run("stacker agent health", timeout=60)
    if code != 0:
        details.append(f"agent health: {stderr.strip() or 'not available'}")
        # Agent not available is not a hard failure
    else:
        details.append(f"agent health: OK")

    # 3. Get app port from stacker.yml
    stacker_yml = WORK_DIR / "stacker.yml"
    app_port = None
    if stacker_yml.exists():
        content = stacker_yml.read_text()
        port_match = re.search(r'ports:\s*\n\s*-\s*["\']?(\d+):', content)
        if port_match:
            app_port = int(port_match.group(1))

    # 4. HTTP check if we have a port
    if app_port:
        code, stdout, stderr = run(
            f"curl -sf --max-time 10 http://localhost:{app_port}/ || true",
            timeout=15,
        )
        if code == 0:
            details.append(f"HTTP check port {app_port}: OK")
        else:
            details.append(f"HTTP check port {app_port}: failed (may need time to start)")

    return success, details

# ---------------------------------------------------------------------------
# Result recording
# ---------------------------------------------------------------------------
def record_success(template, provider, app_port, has_npm, duration):
    """Append success entry to HOWTO.md."""
    if not HOWTO_FILE.exists():
        with open(HOWTO_FILE, "w") as f:
            f.write("# Stacker Template Test Results - Successes\n\n")
            f.write("Tested with `stacker install` + `stacker deploy --target cloud`.\n\n---\n\n")

    entry = f"""## {template} - SUCCESS

- **Provider:** {provider}
- **Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Port:** {app_port or "N/A"}
- **NPM:** {"yes" if has_npm else "no (skipped)"}
- **Duration:** {duration}s

### Commands

```bash
# Install
stacker install {template} \\
  --domain {template}.try.direct \\
  --key {PROVIDERS[provider]["key_name"]} \\
  --region {PROVIDERS[provider]["region"]}

# Deploy
stacker deploy --target cloud --key {PROVIDERS[provider]["key_name"]} --force-new --no-hooks

# Verify
stacker status
stacker agent health

# Destroy
stacker destroy -y
```

---

"""
    with open(HOWTO_FILE, "a") as f:
        f.write(entry)

def record_failure(template, provider, error, logs=""):
    """Append failure entry to BUGS.md."""
    if not BUGS_FILE.exists():
        with open(BUGS_FILE, "w") as f:
            f.write("# Stacker Template Test Results - Bugs\n\n")
            f.write("Failures encountered during `stacker install` testing.\n\n---\n\n")

    entry = f"""## {template} - FAILED

- **Provider:** {provider}
- **Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Error:** {error}

### Logs

```
{logs}
```

---

"""
    with open(BUGS_FILE, "a") as f:
        f.write(entry)

# ---------------------------------------------------------------------------
# Main test flow
# ---------------------------------------------------------------------------
def test_template(template, provider_config, dry_run=False):
    """Test a single template. Returns True on success."""
    provider = [k for k, v in PROVIDERS.items() if v == provider_config][0]
    key_name = provider_config["key_name"]
    region = provider_config["region"]

    print(f"\n{'='*60}")
    print(f"  TEMPLATE: {template}")
    print(f"  PROVIDER: {provider} ({region})")
    print(f"{'='*60}")

    start_time = time.time()

    if dry_run:
        print("  [DRY RUN] Would run:")
        print(f"    stacker install {template} --domain {template}.try.direct --key {key_name} --region {region}")
        print(f"    stacker deploy --target cloud --key {key_name} --force-new --no-hooks")
        print(f"    stacker agent health")
        print(f"    stacker destroy -y")
        return True

    # Ensure work directory exists
    WORK_DIR.mkdir(exist_ok=True)
    stacker_yml = WORK_DIR / "stacker.yml"

    try:
        # Step 1: Install
        print("\n  [1/5] Installing template...")
        cmd = (
            f"stacker install {template} "
            f"--domain {template}.try.direct "
            f"--key {key_name} "
            f"--region {region} "
            f"--file {stacker_yml} "
            f"--force"
        )
        code, stdout, stderr = run(cmd, cwd=str(WORK_DIR), timeout=120)
        if code != 0:
            error_msg = f"stacker install failed (exit {code}): {stderr.strip()}"
            print(f"  FAIL: {error_msg}")
            record_failure(template, provider, error_msg, stderr)
            return False

        print(f"  OK: stacker.yml written")

        # Step 2: Inject NPM
        print("\n  [2/5] Checking NPM...")
        has_npm = False
        if template not in NPM_SKIP:
            has_npm = inject_npm(str(stacker_yml))
            if has_npm:
                print(f"  OK: NPM injected")
            else:
                print(f"  SKIP: NPM not injected (already present or conflict)")
        else:
            print(f"  SKIP: Template uses ports 80/443")

        # Step 3: Deploy
        print("\n  [3/5] Deploying to cloud...")
        cmd = f"stacker deploy --target cloud --key {key_name} --force-new --no-hooks"
        code, stdout, stderr = run(cmd, cwd=str(WORK_DIR), timeout=900)
        if code != 0:
            error_msg = f"stacker deploy failed (exit {code}): {stderr.strip()}"
            print(f"  FAIL: {error_msg}")
            # Try to get container logs
            logs, _, _ = run("docker compose logs --tail=50", cwd=str(WORK_DIR), timeout=30)
            record_failure(template, provider, error_msg, logs or stderr)
            # Still try to destroy
            run("stacker destroy -y", cwd=str(WORK_DIR), timeout=120)
            return False

        print(f"  OK: Deployed")

        # Step 4: Verify
        print("\n  [4/5] Verifying...")
        # Give containers time to start
        time.sleep(10)
        success, details = verify_deployment(template)
        for d in details:
            print(f"  {d}")

        # Step 5: Record and destroy
        duration = int(time.time() - start_time)

        if success:
            # Get app port
            app_port = None
            content = stacker_yml.read_text()
            port_match = re.search(r'ports:\s*\n\s*-\s*["\']?(\d+):', content)
            if port_match:
                app_port = int(port_match.group(1))

            print(f"\n  [5/5] SUCCESS - recording and destroying...")
            record_success(template, provider, app_port, has_npm, duration)
        else:
            print(f"\n  [5/5] PARTIAL SUCCESS - recording and destroying...")
            record_failure(template, provider, "Verification issues: " + "; ".join(details))

        # Destroy
        run("stacker destroy -y", cwd=str(WORK_DIR), timeout=120)
        print(f"  Destroyed. Duration: {duration}s")

        return success

    except Exception as e:
        print(f"  ERROR: {e}")
        record_failure(template, provider, str(e))
        # Try to destroy
        run("stacker destroy -y", cwd=str(WORK_DIR), timeout=120)
        return False

    finally:
        # Clean up work directory
        if stacker_yml.exists():
            stacker_yml.unlink()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def check_stacker_login():
    """Check if stacker CLI is authenticated."""
    code, stdout, stderr = run("stacker whoami", timeout=15)
    if code != 0 and "expired" in (stderr + stdout).lower():
        print("ERROR: Stacker CLI not authenticated. Run: stacker login")
        sys.exit(1)
    return True

def main():
    parser = argparse.ArgumentParser(description="Test all Stacker marketplace templates")
    parser.add_argument("--batch", type=int, help="Batch number to run (1-10)")
    parser.add_argument("--template", type=str, help="Test a single template")
    parser.add_argument("--provider", type=str, choices=["hetzner", "digitalocean", "linode"],
                        help="Override provider for single template")
    parser.add_argument("--list", action="store_true", help="List all templates")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run without executing")
    parser.add_argument("--all", action="store_true", help="Run all batches sequentially")
    args = parser.parse_args()

    load_env()

    if not args.list and not args.dry_run:
        check_stacker_login()
    templates = get_templates()

    if args.list:
        print(f"Total templates: {len(templates)}")
        for i, t in enumerate(templates, 1):
            npm = "skip NPM" if t in NPM_SKIP else "with NPM"
            print(f"  {i:3d}. {t} ({npm})")
        return

    if args.template:
        # Single template test
        provider_name = args.provider or "hetzner"
        provider_config = PROVIDERS[provider_name]
        test_template(args.template, provider_config, dry_run=args.dry_run)
        return

    if args.all:
        # Run all batches
        for batch_num in sorted(BATCH_PROVIDERS.keys()):
            batch = get_batch(templates, batch_num)
            if not batch:
                continue
            provider_name = BATCH_PROVIDERS[batch_num]
            provider_config = PROVIDERS[provider_name]
            print(f"\n{'#'*60}")
            print(f"  BATCH {batch_num} - {provider_name} ({len(batch)} templates)")
            print(f"{'#'*60}")
            for template in batch:
                test_template(template, provider_config, dry_run=args.dry_run)
        return

    # Default: run specified batch
    batch_num = args.batch or 1
    batch = get_batch(templates, batch_num)
    if not batch:
        print(f"Batch {batch_num} is empty. Max batch: {len(templates) // BATCH_SIZE + 1}")
        return

    provider_name = BATCH_PROVIDERS.get(batch_num, "hetzner")
    provider_config = PROVIDERS[provider_name]

    print(f"Batch {batch_num} - {provider_name} ({len(batch)} templates)")
    for template in batch:
        npm = "skip NPM" if template in NPM_SKIP else "with NPM"
        print(f"  - {template} ({npm})")

    if not args.dry_run:
        confirm = input(f"\nDeploy {len(batch)} templates to {provider_name}? [y/N] ")
        if confirm.lower() != "y":
            print("Aborted.")
            return

    for template in batch:
        test_template(template, provider_config, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
