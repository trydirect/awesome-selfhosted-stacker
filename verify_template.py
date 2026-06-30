#!/usr/bin/env python3
"""
verify_template.py — Deploy a stacker template, verify it, then clean up.

Usage:
    python verify_template.py <project_dir> [--port <port>] [--timeout <sec>]

Runs:
    1. stacker deploy --target local --force-rebuild
    2. Poll status until all containers up (or timeout)
    3. Check logs for FATAL/PANIC/unhandled errors
    4. HTTP health check on the app port
    5. docker compose down
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error

STACKER_CLI = os.environ.get("STACKER_CLI", "/usr/local/bin/stacker")
POLL_INTERVAL = 10


def run(cmd: str, cwd: str, timeout: int = 300) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=timeout,
        )
        return proc.returncode, proc.stdout or ""
    except subprocess.TimeoutExpired:
        return -1, f"Timed out after {timeout}s"
    except Exception as e:
        return -1, str(e)


def compose_file_path(project_dir: str) -> str:
    return os.path.join(project_dir, ".stacker", "docker-compose.yml")


def verify(project_dir: str, port: int, timeout_sec: int) -> bool:
    name = os.path.basename(project_dir)
    cfp = compose_file_path(project_dir)
    passed = True

    # ── Step 1: Deploy ──────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Verifying: {name}  ({project_dir})")
    print(f"{'='*60}")

    print(f"\n[1/5] Deploying with stacker...")
    rc, out = run(f"{STACKER_CLI} deploy --target local --force-rebuild", cwd=project_dir, timeout=timeout_sec)
    if rc != 0:
        print(f"  DEPLOY FAILED (exit {rc})")
        print(out[-1000:])
        return False
    print(f"  Deploy command OK")

    # ── Step 2: Poll status ─────────────────────────────────────
    print(f"\n[2/5] Polling status (up to {timeout_sec}s)...")
    deadline = time.time() + timeout_sec
    all_up = False
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)
        rc, out = run(f"{STACKER_CLI} status", cwd=project_dir, timeout=30)
        if rc != 0:
            continue
        lines = out.strip().split("\n")
        # Parse table: skip header and separator lines
        services = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 6 and parts[0].startswith("stacker-"):
                services.append({
                    "name": parts[0],
                    "status": " ".join(parts[5:]),
                })
        if not services:
            continue
        print(f"  Containers: {len(services)}")
        for s in services:
            print(f"    {s['name']:35} {s['status'][:50]}")
        all_up = all("Up" in s["status"] and "Restarting" not in s["status"] for s in services)
        if all_up:
            print(f"  All containers Up!")
            break
        # Check if any are restarting (likely crashed)
        crashing = any("Restarting" in s["status"] for s in services)
        if crashing:
            print(f"  Some containers restarting — likely crash")
            break

    if not all_up:
        print(f"  TIMEOUT or CRASH — not all containers healthy")
        passed = False

    # ── Step 3: Check logs for errors ────────────────────────────
    print(f"\n[3/5] Checking logs for errors...")
    if os.path.exists(cfp):
        rc, out = run(f"docker compose -f {cfp} logs --tail=200", cwd=project_dir, timeout=60)
        log_text = out
        fatal_patterns = [r'\bFATAL\b', r'\bPANIC\b', r'unhandled exception', r'Traceback', r'Error:']
        has_errors = False
        for pat in fatal_patterns:
            matches = re.findall(pat, log_text, re.IGNORECASE)
            if matches:
                # Filter false positives (e.g. "FATAL:" in log level labels)
                if pat == r'\bFATAL\b':
                    if 'level:fatal' in log_text or 'FATAL' in log_text:
                        has_errors = True
                        print(f"  Found fatal-level log entries")
                else:
                    has_errors = True
                    print(f"  Found {len(matches)} matches for '{pat}'")
        if has_errors:
            print(f"  ERROR: Fatal errors in logs!")
            passed = False
        else:
            print(f"  No fatal errors found")
    else:
        print(f"  No compose file at {cfp}")
        passed = False

    # ── Step 4: HTTP health check ────────────────────────────────
    print(f"\n[4/5] HTTP health check on port {port}...")
    health_urls = [
        f"http://localhost:{port}/health",
        f"http://localhost:{port}/healthz",
        f"http://localhost:{port}/",
        f"http://localhost:{port}/_health",
        f"http://localhost:{port}/status",
    ]
    http_ok = False
    for url in health_urls:
        try:
            req = urllib.request.Request(url, method="HEAD")
            resp = urllib.request.urlopen(req, timeout=5)
            if resp.status < 500:
                print(f"  ✓ {url} → {resp.status}")
                http_ok = True
                break
        except urllib.error.HTTPError as e:
            if e.code < 500:
                print(f"  ✓ {url} → {e.code}")
                http_ok = True
                break
            else:
                print(f"  ✗ {url} → {e.code}")
        except Exception as e:
            print(f"  ✗ {url} → {e}")
    if not http_ok:
        # Try GET if HEAD didn't work
        for url in health_urls:
            try:
                resp = urllib.request.urlopen(url, timeout=5)
                if resp.status < 500:
                    print(f"  ✓ {url} → {resp.status}")
                    http_ok = True
                    break
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    print(f"  ✓ {url} → {e.code}")
                    http_ok = True
                    break
            except Exception:
                pass
    if not http_ok:
        print(f"  WARNING: No HTTP endpoint responded on port {port}")
        # Don't fail for non-HTTP services like Pi-hole (DNS)

    # ── Step 5: Clean up ─────────────────────────────────────────
    print(f"\n[5/5] Cleaning up (docker compose down)...")
    if os.path.exists(cfp):
        rc, out = run(f"docker compose -f {cfp} down -v", cwd=project_dir, timeout=60)
        print(f"  Cleanup {'OK' if rc == 0 else f'FAILED (exit {rc})'}")
    else:
        print(f"  No compose file to clean up")

    verdict = "PASS" if passed else "FAIL"
    print(f"\n{'─'*60}")
    print(f"  VERDICT: {verdict}  ({name})")
    print(f"{'─'*60}\n")
    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify a stacker template")
    parser.add_argument("project_dir", help="Path to the project directory with stacker.yml")
    parser.add_argument("--port", type=int, default=8000, help="App HTTP port to check (default: 8000)")
    parser.add_argument("--timeout", type=int, default=300, help="Deploy timeout in seconds (default: 300)")
    args = parser.parse_args()

    if not os.path.exists(os.path.join(args.project_dir, "stacker.yml")):
        print(f"Error: no stacker.yml in {args.project_dir}")
        return 1

    success = verify(args.project_dir, args.port, args.timeout)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
