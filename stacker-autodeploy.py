#!/usr/bin/env python3
"""
stacker-autodeploy.py

Multi-agent system for automated stack creation using stacker-cli.
Searches GitHub for a popular OSS project, reads its Docker setup,
generates stacker.yml, deploys locally, and verifies health.

Agents
------
  Research Agent      — finds popular OSS repos with Dockerfile + docker-compose
  Stacker Specialist  — reads Docker files, generates stacker.yml, deploys
  QA Tester           — verifies all services are healthy
  Rust Developer      — analyzes errors and suggests/writes stacker CLI fixes

Usage
-----
  python stacker-autodeploy.py [--env .env] [--lang python|nodejs|rust|go]
  python stacker-autodeploy.py --env credentials.env --lang nodejs
  python stacker-autodeploy.py --mcp                 # use Stacker MCP for tools

Env vars (or .env file)
-----------------------
  OLLAMA_HOST         Ollama base URL (default: http://localhost:11434)
  OLLAMA_MODEL        model name (default: qwen2.5:7b)
  GITHUB_TOKEN        optional but recommended (avoids rate limits)
  STACKER_CLI         path to stacker-cli binary (default: stacker-cli)
  STACKER_MCP_URL     Stacker MCP WebSocket URL (default: wss://stacker.try.direct/mcp)
  STACKER_TOKEN       Bearer token for MCP auth (default: read from credentials.json)
  ANTHROPIC_API_KEY   Anthropic API key — use Claude instead of Ollama
  ANTHROPIC_MODEL     Claude model override (default: claude-haiku-4-5-20251001)
  HETZNER_TOKEN       Hetzner Cloud API token — enables Phase 5 cloud deploy
  HCLOUD_TOKEN        alias for HETZNER_TOKEN (both accepted)
  CLOUD_REGION        Hetzner region (default: fsn1)
  CLOUD_SIZE          Hetzner server type (default: cx21)
  SSH_KEY_PATH        SSH key stacker uploads to Hetzner (default: ~/.ssh/id_ed25519)

Dependencies
------------
  pip install requests
  pip install websockets   # only needed with --mcp
"""

from __future__ import annotations

import argparse
import base64
import functools
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

import requests

# ── Constants ──────────────────────────────────────────────────────────────────

GH_DELAY = 1.0  # seconds between GitHub API requests (avoids unauthenticated rate limit)

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:7b"
DEFAULT_WORK_DIR = "./stacker-projects"
DEFAULT_STACKER_SRC = Path(__file__).parent.parent / "try.direct" / "stacker"

GITHUB_API = "https://api.github.com"
DEFAULT_MCP_URL = "wss://stacker.try.direct/mcp"

DEFAULT_CLOUD_REGION = "fsn1"   # Hetzner Falkenstein — lowest latency for EU
DEFAULT_CLOUD_SIZE   = "cx22"   # 2 vCPU / 4 GB RAM — Hetzner current gen (cx21 was retired)
DEFAULT_SSH_KEY_PATH = str(Path.home() / ".ssh" / "id_ed25519")

# Known-good repos per language — verified to have Dockerfile + docker-compose.yml at root.
# Used as fallback when GitHub search + model can't find a valid candidate.
# Verified 2026-06-02: each entry confirmed to have Dockerfile AND compose at the
# listed path. Put the most self-contained / fastest-starting repos first.
KNOWN_REPOS: dict[str, list[dict]] = {
    "python": [
        # Verified: Dockerfile + docker-compose.yml at root
        {"owner": "ArchiveBox",        "repo": "ArchiveBox",     "compose_path": "docker-compose.yml"},
    ],
    "nodejs": [
        # Verified: Dockerfile + docker-compose.yml at root
        {"owner": "outline",           "repo": "outline",        "compose_path": "docker-compose.yml"},
    ],
    "typescript": [
        {"owner": "outline",           "repo": "outline",        "compose_path": "docker-compose.yml"},
    ],
    "rust": [
        # meilisearch has Dockerfile but no compose in root — skipped
        # vaultwarden same — skipped
        # Add here once a verified rust repo is confirmed
    ],
    "go": [
        # Add verified go repos here
    ],
}

# Map CLI --lang argument to GitHub language label
LANG_TO_GITHUB = {
    "python": "Python",
    "nodejs": "JavaScript",
    "typescript": "TypeScript",
    "rust": "Rust",
    "go": "Go",
}

# Map GitHub language to stacker app type
LANG_TO_APP_TYPE = {
    "Python": "python",
    "JavaScript": "node",
    "TypeScript": "node",
    "Rust": "rust",
    "Go": "go",
}

# ── Stacker MCP client ─────────────────────────────────────────────────────────

def read_stacker_token() -> Optional[str]:
    """Read the access_token from ~/.config/stacker/credentials.json (or macOS equivalent)."""
    if platform.system() == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    creds_path = base / "stacker" / "credentials.json"
    try:
        with open(creds_path) as f:
            return json.load(f).get("access_token")
    except Exception:
        return None


class StackerMcpClient:
    """
    Thin WebSocket MCP client for the Stacker API.

    Usage (context manager keeps the connection open for the session):
        with StackerMcpClient(url, token) as mcp:
            tools = mcp.tools          # list[dict] — raw MCP Tool objects
            result = mcp.call("deploy_app", {"project_id": 1})
    """

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self._ws = None
        self._tools: list[dict] = []

    def __enter__(self) -> "StackerMcpClient":
        try:
            from websockets.sync.client import connect as ws_connect
        except ImportError:
            raise SystemExit("websockets library required for --mcp: pip install 'websockets>=12.0'")
        # Token can go as query param (web UI style) or Authorization header.
        # The TryDirect web UI uses: wss://host/mcp?access_token=<token>
        connect_url = self.url
        if self.token and "access_token" not in connect_url:
            sep = "&" if "?" in connect_url else "?"
            connect_url = f"{connect_url}{sep}access_token={self.token}"
        self._ws = ws_connect(
            connect_url,
            additional_headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
            open_timeout=15,
        )
        self._initialize()
        self._tools = self._list_tools()
        print(f"  MCP connected — {len(self._tools)} tools available")
        return self

    def __exit__(self, *_) -> None:
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass

    # ── Low-level JSON-RPC ─────────────────────────────────────────────────────

    def _send(self, method: str, params: Optional[dict] = None, req_id: Optional[str] = None) -> None:
        msg: dict = {"jsonrpc": "2.0", "method": method}
        if req_id is not None:
            msg["id"] = req_id
        if params is not None:
            msg["params"] = params
        self._ws.send(json.dumps(msg))

    def _recv_result(self, req_id: str) -> dict:
        """Wait for the JSON-RPC response matching req_id (skip notifications)."""
        while True:
            raw = self._ws.recv(timeout=30)
            resp = json.loads(raw)
            if resp.get("id") != req_id:
                continue  # notification or different request
            if "error" in resp:
                err = resp["error"]
                raise RuntimeError(f"MCP error {err.get('code')}: {err.get('message')}")
            return resp.get("result") or {}

    def _rpc(self, method: str, params: Optional[dict] = None) -> dict:
        req_id = uuid.uuid4().hex[:8]
        self._send(method, params, req_id)
        return self._recv_result(req_id)

    # ── MCP handshake ──────────────────────────────────────────────────────────

    def _initialize(self) -> None:
        self._rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "stacker-autodeploy", "version": "1.0"},
        })
        self._send("notifications/initialized")  # no response expected

    def _list_tools(self) -> list[dict]:
        result = self._rpc("tools/list")
        return result.get("tools", [])

    # ── Public API ─────────────────────────────────────────────────────────────

    @property
    def tools(self) -> list[dict]:
        return self._tools

    def call(self, name: str, arguments: dict) -> str:
        """Call an MCP tool and return the text content."""
        result = self._rpc("tools/call", {"name": name, "arguments": arguments})
        parts = [
            c["text"]
            for c in result.get("content", [])
            if c.get("type") == "text"
        ]
        is_error = result.get("isError", False)
        text = "\n".join(parts) or "(empty response)"
        if is_error:
            text = f"[MCP tool error] {text}"
        return text

    def as_ollama_tools(self, only: Optional[set] = None) -> list[dict]:
        """Convert MCP tool list to Ollama/OpenAI tool format.

        Pass `only={"tool_a", "tool_b"}` to return a filtered subset —
        keeps payload size reasonable when the model doesn't need all 100+ tools.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("inputSchema", {}),
                },
            }
            for t in self._tools
            if only is None or t["name"] in only
        ]

    def make_handler(self, *, project_dir: str, stacker_src: str, github_token: Optional[str]):
        """
        Return a tool_fn compatible with run_agent().

        MCP tools are called through the WebSocket; local tools (write_file,
        read_file, run_shell, grep_src) are handled in-process so local deploy
        and file operations still work alongside cloud MCP tools.
        """
        local_handler = make_handler(
            github_token=github_token,
            project_dir=project_dir,
            stacker_src=stacker_src,
        )
        LOCAL_TOOLS = {"write_file", "read_file", "run_shell", "grep_src",
                       "read_github_file", "search_github", "check_repo_files"}

        def handle(name: str, inputs: dict) -> str:
            if name in LOCAL_TOOLS:
                return local_handler(name, inputs)
            return self.call(name, inputs)

        return handle


# ── .env loader ────────────────────────────────────────────────────────────────

def load_env_file(path: str) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return result


# ── GitHub helpers ─────────────────────────────────────────────────────────────

def _gh_headers(token: Optional[str]) -> dict:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def validate_github_token(token: Optional[str]) -> Optional[str]:
    """Return token if valid, None if rejected (avoids 401s on every request)."""
    if not token:
        return None
    try:
        resp = requests.get(f"{GITHUB_API}/user", headers=_gh_headers(token), timeout=10)
        if resp.status_code == 401:
            print("  GitHub token invalid (401) — falling back to unauthenticated access (60 req/hr limit)")
            return None
    except Exception:
        pass
    return token


class GitHubRateLimitError(Exception):
    """Raised when GitHub returns 403 rate-limit. Repos checked after this point
    should NOT be saved to .visited — we never actually checked their files."""


def _gh_get(url: str, token: Optional[str], **kwargs) -> requests.Response:
    """GET with automatic 403 rate-limit detection."""
    resp = requests.get(url, headers=_gh_headers(token), **kwargs)
    if resp.status_code == 403:
        reset = resp.headers.get("X-RateLimit-Reset", "?")
        raise GitHubRateLimitError(
            f"GitHub rate limit hit — resets at epoch {reset}. "
            "Add a valid GITHUB_TOKEN to .env for higher limits."
        )
    return resp


def gh_search_repos(language: str, token: Optional[str], min_stars: int = 500) -> list[dict]:
    query = f"language:{language} topic:docker stars:>{min_stars} fork:false"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": 10}
    try:
        resp = _gh_get(f"{GITHUB_API}/search/repositories", token, params=params, timeout=15)
        resp.raise_for_status()
    except GitHubRateLimitError:
        raise
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"GitHub search failed ({exc.response.status_code}). "
            "Add a valid GITHUB_TOKEN to .env for higher rate limits."
        ) from exc
    return resp.json().get("items", [])


def gh_file_exists(owner: str, repo: str, path: str, token: Optional[str]) -> bool:
    resp = _gh_get(f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}", token, timeout=10)
    return resp.status_code == 200


def gh_read_file(owner: str, repo: str, path: str, token: Optional[str]) -> Optional[str]:
    resp = _gh_get(f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}", token, timeout=10)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if isinstance(data, list):
        return f"[directory with {len(data)} entries]"
    if data.get("encoding") == "base64":
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    return data.get("content")


# ── Shell helper ───────────────────────────────────────────────────────────────

def run_shell(cmd: str, cwd: str, timeout: int = 120, env: Optional[dict] = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=timeout,
            env=env,
        )
        return proc.returncode, (proc.stdout or "")[:6000]
    except subprocess.TimeoutExpired:
        return -1, f"Timed out after {timeout}s"
    except Exception as exc:
        return -1, str(exc)


# ── Notification ───────────────────────────────────────────────────────────────

def notify(title: str, body: str) -> None:
    print(f"\n*** {title}: {body}")
    try:  # macOS
        subprocess.run(
            ["osascript", "-e", f'display notification "{body}" with title "{title}"'],
            check=False, timeout=3,
        )
    except Exception:
        pass


# ── Cloud / Hetzner helpers ────────────────────────────────────────────────────

def add_cloud_config_to_stacker_yml(
    project_dir: str, region: str, size: str, ssh_key: str,
    public_ports: Optional[list[str]] = None,
) -> bool:
    """Inject a cloud: sub-section into the deploy: block of stacker.yml.

    Replaces the whole deploy: block so the file can be used for both local
    (stacker deploy --target local) and cloud (stacker deploy --target cloud)
    without being rewritten each time.
    """
    stacker_yml = os.path.join(project_dir, "stacker.yml")
    try:
        with open(stacker_yml) as f:
            content = f.read()
    except FileNotFoundError:
        return False

    cloud_deploy_block = (
        "deploy:\n"
        "  target: local\n"
        "  cloud:\n"
        f"    provider: hetzner\n"
        f"    region: {region}\n"
        f"    size: {size}\n"
        f"    ssh_key: {ssh_key}\n"
    )
    if public_ports:
        cloud_deploy_block += (
            "    public_ports:\n" +
            "".join(f"      - \"{p}\"\n" for p in public_ports)
        )
    # Replace the existing deploy: block (everything from 'deploy:' to the
    # next top-level key or end-of-file).
    new_content = re.sub(
        r'^deploy:.*?(?=^\S|\Z)',
        cloud_deploy_block,
        content,
        flags=re.MULTILINE | re.DOTALL,
    )
    with open(stacker_yml, "w") as f:
        f.write(new_content)
    return True


def get_cloud_server_ip(project_dir: str, stacker_cmd: str) -> Optional[str]:
    """Return the public IPv4 of the cloud server stacker provisioned.

    Stacker manages the server — no Hetzner API call needed here.
    Checks the lock file stacker writes (--lock flag), then falls back to
    parsing `stacker status` output.
    """
    for lock_name in ("deployment-cloud.lock", "deployment.lock", "lock.json"):
        lock_path = os.path.join(project_dir, ".stacker", lock_name)
        if os.path.exists(lock_path):
            try:
                data = json.loads(open(lock_path).read())
                for key in ("ip", "server_ip", "public_ip", "ipv4", "host"):
                    val = data.get(key)
                    if val and re.match(r'\d+\.\d+\.\d+\.\d+', str(val)):
                        return str(val)
            except Exception:
                pass

    _, out = run_shell(f"{stacker_cmd} status", cwd=project_dir, timeout=30)
    for token in re.findall(r'\b(\d{1,3}(?:\.\d{1,3}){3})\b', out):
        if not token.startswith(("127.", "0.", "10.", "172.", "192.168.")):
            return token

    return None


# ── Ollama client ──────────────────────────────────────────────────────────────

def ollama_chat(
    host: str,
    model: str,
    messages: list[dict],
    tools: Optional[list[dict]] = None,
    timeout: int = 120,
    api_key: Optional[str] = None,
) -> dict:
    """POST to the chat endpoint and return a normalised response dict.

    Probe order (persisted across calls via module-level flags):
      1. {host}/api/chat                   — Ollama native
      2. {host}/api/chat  without tools    — Ollama, tool-call fallback
      3. {host}/v1/chat/completions        — OpenAI-compatible proxy
      4. {host}/v1/chat/completions no tools

    Response is normalised to Ollama shape: {"message": {"role", "content", "tool_calls"}}
    """
    global _tools_blocked, _use_openai_compat

    headers: dict = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    def _post_ollama(with_tools: bool) -> requests.Response:
        payload: dict = {"model": model, "messages": messages, "stream": False}
        if with_tools and tools:
            payload["tools"] = tools
        return requests.post(f"{host}/api/chat", headers=headers, json=payload, timeout=timeout)

    def _post_openai(with_tools: bool) -> requests.Response:
        payload: dict = {"model": model, "messages": messages, "stream": False}
        if with_tools and tools:
            payload["tools"] = tools
        return requests.post(f"{host}/v1/chat/completions", headers=headers, json=payload, timeout=timeout)

    def _to_ollama_shape(resp: requests.Response, openai: bool) -> dict:
        """Normalise OpenAI response to Ollama shape."""
        if not openai:
            return resp.json()
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})
        # OpenAI tool_calls → Ollama tool_calls shape
        raw_tcs = msg.get("tool_calls") or []
        tool_calls = [
            {"function": {"name": tc["function"]["name"],
                          "arguments": tc["function"].get("arguments", {})}}
            for tc in raw_tcs
        ]
        return {
            "message": {
                "role": msg.get("role", "assistant"),
                "content": msg.get("content") or "",
                "tool_calls": tool_calls or None,
            },
            "done_reason": "tool_calls" if tool_calls else "stop",
        }

    # ── attempt 1: native Ollama with tools ───────────────────────
    if not _use_openai_compat and not _tools_blocked:
        resp = _post_ollama(with_tools=True)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 405:
            # Try without tools first
            resp2 = _post_ollama(with_tools=False)
            if resp2.status_code == 200:
                _tools_blocked = True
                print("  [ollama] tools rejected (405) — text-mode tool calls active")
                return resp2.json()
            # /api/chat itself is blocked — switch to OpenAI compat
            _use_openai_compat = True
            print("  [ollama] /api/chat blocked (405) — switching to /v1/chat/completions")
        else:
            resp.raise_for_status()

    # ── attempt 2: native Ollama without tools ────────────────────
    if not _use_openai_compat and _tools_blocked:
        resp = _post_ollama(with_tools=False)
        if resp.status_code != 405:
            resp.raise_for_status()
            return resp.json()
        _use_openai_compat = True
        print("  [ollama] /api/chat fully blocked — switching to /v1/chat/completions")

    # ── attempt 3/4: OpenAI-compatible endpoint ───────────────────
    resp = _post_openai(with_tools=(not _tools_blocked))
    if resp.status_code == 405 and not _tools_blocked:
        _tools_blocked = True
        print("  [openai-compat] tools rejected (405) — text-mode tool calls active")
        resp = _post_openai(with_tools=False)
    resp.raise_for_status()
    return _to_ollama_shape(resp, openai=True)


_tools_blocked: bool = False        # tools rejected by endpoint
_use_openai_compat: bool = False    # /api/chat blocked; use /v1/chat/completions


def _wrap_tools(tools: list[dict]) -> list[dict]:
    """Convert tool defs (MCP or internal) to Ollama/OpenAI format.

    Handles both MCP's camelCase 'inputSchema' and internal 'input_schema'/'parameters'.
    Skips tools already in OpenAI format (have 'type'=='function').
    """
    wrapped = []
    for t in tools:
        if t.get("type") == "function":
            wrapped.append(t)  # already in OpenAI format (e.g. from as_ollama_tools())
            continue
        schema = t.get("inputSchema") or t.get("input_schema") or t.get("parameters") or {}
        wrapped.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": schema,
            },
        })
    return wrapped


def _extract_text_tool_calls(content: str, known_tools: list[dict]) -> list[dict]:
    """
    Fallback for models that emit tool calls as plain text instead of structured
    tool_calls. Handles three patterns:

    Pattern 1 — bare JSON object (single):
        {"name": "search_github", "arguments": {"language": "Python"}}

    Pattern 2 — multiple JSON objects, one per line (NDJSON):
        {"name": "read_github_file", "arguments": {...}}
        {"name": "read_github_file", "arguments": {...}}

    Pattern 3 — JSON inside a code block (single or NDJSON):
        ```json
        {"name": "search_github", "arguments": {...}}
        ```
    """
    tool_names = {t["name"] for t in known_tools}
    candidates: list[dict] = []
    seen: set[str] = set()

    def _try(text: str) -> None:
        text = text.strip()
        if not text:
            return
        try:
            obj = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return
        if not isinstance(obj, dict):
            return
        name = obj.get("name") or obj.get("function", {}).get("name")
        args = obj.get("arguments") or obj.get("args") or obj.get("parameters") or {}
        if name and name in tool_names:
            key = f"{name}:{json.dumps(args, sort_keys=True)}"
            if key not in seen:
                seen.add(key)
                candidates.append({"function": {"name": name, "arguments": args}})

    def _scan_block(block: str) -> None:
        # Try the whole block first
        _try(block)
        # Then try each line individually (NDJSON)
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("{"):
                _try(line)

    # Bare content (single or NDJSON)
    _scan_block(content)

    # Code blocks
    for m in re.finditer(r'```(?:\w+)?\s*(.*?)\s*```', content, re.DOTALL):
        _scan_block(m.group(1))

    return candidates


# ── Agent runner ───────────────────────────────────────────────────────────────

def run_agent(
    *,
    label: str,
    ollama_host: str,
    ollama_model: str,
    ollama_api_key: Optional[str] = None,
    system: str,
    user_msg: str,
    tools: list[dict],
    tool_fn,
    max_turns: int = 15,
) -> str:
    """Agentic loop: run an Ollama model with tools until done or max_turns."""
    print(f"\n{'─'*62}")
    print(f"  Agent: {label}  [{ollama_model}]")
    print(f"{'─'*62}")

    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]
    wrapped_tools = _wrap_tools(tools) if tools else None
    final_text = ""

    for turn in range(max_turns):
        data = ollama_chat(ollama_host, ollama_model, messages, wrapped_tools, api_key=ollama_api_key)
        msg = data.get("message", {})
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls") or []

        # Fallback: some models (e.g. qwen2.5-coder) emit tool calls as plain
        # text JSON instead of using the structured tool_calls field.
        text_based = False
        if not tool_calls and content and tools:
            tool_calls = _extract_text_tool_calls(content, tools)
            text_based = bool(tool_calls)

        if content and not text_based:
            # Only print/store content that isn't just a raw tool-call blob
            print(f"[{label}] {content[:600]}" + ("…" if len(content) > 600 else ""))
            final_text = content

        if not tool_calls:
            break

        # Append assistant turn (omit content when it was just the raw call JSON)
        messages.append({
            "role": "assistant",
            "content": "" if text_based else content,
            "tool_calls": tool_calls,
        })

        # Execute each tool call and append results
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            arguments = fn.get("arguments", {})
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            args_preview = json.dumps(arguments)[:120]
            print(f"  [tool:{name}] {args_preview}")
            result_str = str(tool_fn(name, arguments))[:8000]
            print(f"  → {result_str[:200]}" + ("…" if len(result_str) > 200 else ""))

            messages.append({"role": "tool", "name": name, "content": result_str})

    return final_text


def _normalize_tool_schema(schema: Optional[dict]) -> dict:
    """Ensure a JSON Schema is a valid Anthropic input_schema (must be type:object)."""
    if not schema or not isinstance(schema, dict):
        return {"type": "object", "properties": {}}
    result = dict(schema)
    if result.get("type") != "object":
        result["type"] = "object"
    if "properties" not in result:
        result["properties"] = {}
    return result


def run_agent_anthropic(
    *,
    label: str,
    anthropic_model: str,
    anthropic_api_key: str,
    system: str,
    user_msg: str,
    tools: list[dict],
    tool_fn,
    max_turns: int = 15,
) -> str:
    """Agentic loop using Anthropic Messages API (claude-haiku / claude-sonnet / etc.)."""
    print(f"\n{'─'*62}")
    print(f"  Agent: {label}  [{anthropic_model}]")
    print(f"{'─'*62}")

    # Convert Ollama/OpenAI tool format → Anthropic format
    anthropic_tools: Optional[list[dict]] = None
    if tools:
        anthropic_tools = []
        for t in tools:
            if t.get("type") == "function":
                fn = t["function"]
                anthropic_tools.append({
                    "name": fn["name"],
                    "description": (fn.get("description") or "")[:1024],
                    "input_schema": _normalize_tool_schema(fn.get("parameters")),
                })
            else:
                raw_schema = (
                    t.get("inputSchema") or t.get("input_schema") or
                    t.get("parameters")
                )
                anthropic_tools.append({
                    "name": t["name"],
                    "description": (t.get("description") or "")[:1024],
                    "input_schema": _normalize_tool_schema(raw_schema),
                })

    headers = {
        "x-api-key": anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    messages: list[dict] = [{"role": "user", "content": user_msg}]
    final_text = ""

    for turn in range(max_turns):
        payload: dict = {
            "model": anthropic_model,
            "max_tokens": 4096,
            "system": system,
            "messages": messages,
        }
        if anthropic_tools:
            payload["tools"] = anthropic_tools

        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=120,
        )
        if not resp.ok:
            print(f"  [Anthropic {resp.status_code}] {resp.text[:800]}")
            resp.raise_for_status()
        data = resp.json()

        content_blocks = data.get("content", [])
        stop_reason = data.get("stop_reason", "end_turn")

        text_parts = [b["text"] for b in content_blocks if b.get("type") == "text"]
        tool_use_blocks = [b for b in content_blocks if b.get("type") == "tool_use"]

        text = "".join(text_parts)
        if text:
            print(f"[{label}] {text[:600]}" + ("…" if len(text) > 600 else ""))
            final_text = text

        if stop_reason != "tool_use" or not tool_use_blocks:
            break

        # Append assistant turn (content_blocks preserves tool_use ids)
        messages.append({"role": "assistant", "content": content_blocks})

        # Execute tools and collect tool_result content blocks
        tool_results = []
        for block in tool_use_blocks:
            name = block["name"]
            inputs = block.get("input", {})
            tool_use_id = block["id"]

            args_preview = json.dumps(inputs)[:120]
            print(f"  [tool:{name}] {args_preview}")
            result_str = str(tool_fn(name, inputs))[:8000]
            print(f"  → {result_str[:200]}" + ("…" if len(result_str) > 200 else ""))

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": result_str,
            })

        messages.append({"role": "user", "content": tool_results})

    return final_text


# ── Tool definitions ───────────────────────────────────────────────────────────

TOOLS_RESEARCH = [
    {
        "name": "search_github",
        "description": "Search GitHub for popular repositories by language",
        "input_schema": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "e.g. Python, JavaScript, Rust, Go"},
                "min_stars": {"type": "integer", "default": 500},
            },
            "required": ["language"],
        },
    },
    {
        "name": "check_repo_files",
        "description": "Check which files exist in a GitHub repo",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "File paths to check, e.g. ['Dockerfile', 'docker-compose.yml']",
                },
            },
            "required": ["owner", "repo", "paths"],
        },
    },
]

TOOLS_SPECIALIST = [
    {
        "name": "read_github_file",
        "description": "Read a file from a GitHub repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "path": {"type": "string"},
            },
            "required": ["owner", "repo", "path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a local file (creates parent directories)",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative to project dir or absolute"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a local file",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "run_shell",
        "description": "Run a shell command in the project directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {"type": "integer", "default": 180, "description": "Seconds"},
            },
            "required": ["command"],
        },
    },
]

TOOLS_QA = [
    {
        "name": "run_shell",
        "description": "Run a shell command",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {"type": "integer", "default": 30},
            },
            "required": ["command"],
        },
    },
]

TOOLS_RUST_DEV = [
    {
        "name": "read_file",
        "description": (
            "Read a source file from the stacker codebase. "
            "Use line_offset + line_limit to paginate large files — "
            "the response header shows total line count."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "line_offset": {"type": "integer", "default": 0, "description": "Start at this line (0-indexed)"},
                "line_limit": {"type": "integer", "default": 150, "description": "Number of lines to return"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "grep_src",
        "description": (
            "Grep stacker source code with extended regex (-E). "
            "Supports alternation: 'foo|bar'. "
            "Returns file:line matches."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Extended regex pattern, e.g. 'compose.*up|docker.*run'"},
                "directory": {"type": "string", "default": "src/"},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "write_file",
        "description": "Write a Rust source fix",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
]

# MCP tool subsets — curated per phase so the payload stays small.
# Sending all 100+ MCP tools at once exceeds typical proxy/model limits.
MCP_TOOLS_SPECIALIST = {
    "validate_stack_config",      # validate stacker.yml before deploy
    "recommend_stack_services",   # suggest services for the app type
    "discover_stack_services",    # parse compose → service list
    "get_docker_compose_yaml",    # retrieve generated compose from stacker
    "list_pipe_templates",        # show available pipe connection patterns
    "list_projects",              # list registered Stacker projects
    "get_project",                # fetch project details
}

MCP_TOOLS_QA = {
    "get_deployment_status",      # check deployment state
    "get_deployment_state",       # detailed runtime state
    "get_container_logs",         # fetch container logs
    "list_containers",            # list running containers
    "get_container_health",       # healthcheck status
    "get_error_summary",          # summarise errors from deployment
}


# ── System prompts ─────────────────────────────────────────────────────────────

SYSTEM_RESEARCH = """\
You are a Research Agent specializing in open-source project discovery.

Your goal: find ONE open-source web application on GitHub that is ideal for a local
Docker deployment demonstration using stacker-cli.

Selection criteria (all must be met):
- Has BOTH a Dockerfile AND a docker-compose.yml (or compose.yml) in the repo root
- Stars ≥ 500
- Primary language: as requested by the user
- Self-contained: runs with docker compose up, no external cloud dependencies
- Simple enough that all services spin up within 2–3 minutes locally
- Preferably has a web UI or REST API (not just a CLI tool)
- Avoid repos that require hardware (GPUs, IoT) or paid SaaS

Steps:
1. Search GitHub for repos matching the language criteria
2. For the top candidates, verify they have Dockerfile AND docker-compose.yml
3. Pick the best candidate (simple, popular, self-contained)

Return your choice as a JSON block (no surrounding text):
```json
{
  "owner": "...",
  "repo": "...",
  "full_name": "owner/repo",
  "description": "...",
  "language": "...",
  "stars": 1234,
  "dockerfile_path": "Dockerfile",
  "compose_path": "docker-compose.yml"
}
```
"""

SYSTEM_SPECIALIST = """\
You are a Stacker CLI Specialist — an expert at deploying applications locally
using stacker-cli.

Your workflow:
1. Inspect the Dockerfile and docker-compose.yml provided in the user message
2. Identify ALL services: database (postgres/mysql/mongo), cache (redis/memcached),
   queue (rabbitmq/kafka), storage (minio/s3), and the main app
3. Detect the app type: node, python, rust, go, php, custom
4. Write a stacker.yml to the project directory (filename "stacker.yml" only)
5. Dry-run, then deploy
6. On first failure: immediately check logs BEFORE making changes:
   `docker compose -f .stacker/docker-compose.yml logs --tail=50`
   Read the error, fix the root cause in stacker.yml, then redeploy with --force-rebuild
7. Poll status every 30s up to 5 times
8. Set up one pipe

stacker.yml schema — copy this structure exactly:
```yaml
name: <repo-name>
version: "1.0.0"

app:
  type: python          # one of: node, python, rust, go, php, custom
  path: .
  image: owner/app:tag   # prefer a public upstream image when one exists
  # dockerfile: Dockerfile  # use only when no public app image exists
  ports:
    - "8080:8080"       # host:container
  environment: {}

services:
  - name: postgres
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: "${DB_PASSWORD}"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  - name: redis
    image: redis:7-alpine
    ports:
      - "6379:6379"
    environment: {}
    volumes: []

proxy:
  type: none
  auto_detect: false

deploy:
  target: local
  cloud:
    provider: hetzner
    region: fsn1
    size: cpx22
    # public_ports:        # opt-in: open these in cloud firewall (omit to keep firewall closed)
    #   - "8000"
    #   - "80"

monitoring:
  status_panel: true

env_file: .env
env: {}
```

Critical rules:
- deploy.target MUST be "local"
- monitoring.status_panel MUST be true
- proxy.type should be "none" unless the repo explicitly uses a reverse proxy
- Prefer `app.image` over `app.dockerfile` when the upstream project publishes a public Docker image.
- Use `app.dockerfile` only when there is no public app image or the Dockerfile materially customizes the app.
- Use ${VAR_NAME} for all passwords/secrets from .env
- Never hardcode passwords
- Postgres: postgres:16 | MySQL: mysql:8 | Redis: redis:7-alpine
  Mongo: mongo:7 | RabbitMQ: rabbitmq:3-management | MinIO: minio/minio:latest
- Write ONLY real YAML — never write placeholder text like <value here>

Local deployment rules (CRITICAL — apply these before writing stacker.yml):
- TLS/SSL: for local deploys, DISABLE TLS. If the compose file sets a TLS_PATH, TLS_DIR,
  TLS_CERT, or similar env var, omit it entirely from stacker.yml. Apps typically disable TLS
  when the env var is absent. Never mount a certs volume for local deployments.
- Shell brace expansion: Docker does NOT expand patterns like /data/{0..3} or /path/foo{1..4}.
  Expand them yourself: e.g. VOLUMES=/data/rustfs{0..3} → VOLUMES=/data/rustfs0 /data/rustfs1 /data/rustfs2 /data/rustfs3
- Local-only bypass flags: apps like RustFS, MinIO, etc. have safety checks that fail on a single
  disk (e.g. RUSTFS_UNSAFE_BYPASS_DISK_CHECK, MINIO_VOLUMES on one disk). Read the FATAL error message —
  it usually tells you the bypass env var. Set it for local testing.
- NEVER manually edit .stacker/docker-compose.yml. It is generated by stacker.
  To change volumes, ports, or environment: update stacker.yml and run --force-rebuild.
  Direct edits to .stacker/docker-compose.yml are lost on the next --force-rebuild.
- Remote/cloud note: Stacker does not build and push local Dockerfile images to a registry.
  If you use app.dockerfile, local deploy can work, but cloud deploy needs CI/CD to publish
  the image first and stacker.yml must set app.image to that registry tag.

Init requirements:
- Many apps crash on first start because their data directory isn't initialized.
  Examples: ArchiveBox needs `archivebox init`, Django needs `manage.py migrate`,
  Rails needs `db:setup`, etc.
- Detect: check logs immediately after deploy. If you see "not initialized" / "run init first"
  in logs and the container is restarting, that's an init requirement.
- Fix workflow (CRITICAL — follow this order exactly):
  1. Run initial deploy once to let stacker generate .stacker/Dockerfile.
  2. Write entrypoint.sh to the project dir:
       write_file("entrypoint.sh", "#!/bin/sh\n<init-cmd> || true\nexec <start-cmd>\n")
  3. Append to .stacker/Dockerfile (do NOT use --force-rebuild after this):
       write_file(".stacker/Dockerfile",
         "<existing content>\nCOPY entrypoint.sh /entrypoint.sh\nRUN chmod +x /entrypoint.sh\nENTRYPOINT [\"/entrypoint.sh\"]\n")
  4. Rebuild WITHOUT --force-rebuild (stacker reuses the modified .stacker/Dockerfile):
       run_shell("docker compose -f .stacker/docker-compose.yml build && docker compose -f .stacker/docker-compose.yml up -d")
  NOTE: --force-rebuild regenerates .stacker/Dockerfile from scratch, erasing your changes.
  NOTE: write_file paths are relative to the project directory (e.g. ".stacker/Dockerfile" is correct).
"""

SYSTEM_QA = """\
You are a QA Engineer verifying a Docker stack deployment.

Run these checks in order:
1. docker compose -f .stacker/docker-compose.yml ps
   → All services must be in state "running" (not "exit", "restarting", or "created")
2. docker compose -f .stacker/docker-compose.yml logs --tail=100
   → Look for FATAL, PANIC, or unhandled exception lines
3. For each exposed HTTP port, attempt a curl health check:
   curl -sf http://localhost:<port>/health || curl -sf http://localhost:<port>/healthz
   || curl -sf http://localhost:<port>/ -o /dev/null -w "%{http_code}"

Verdict:
- PASS: all containers running, no fatal errors in logs, at least one HTTP check succeeded
- FAIL: any container not running OR fatal errors found

Return your verdict clearly:
```
QA VERDICT: PASS|FAIL
Details: <brief explanation>
```
"""

SYSTEM_RUST_DEV = """\
You are a senior Rust developer on the stacker-cli team.

Given a deployment failure report, first determine whether the failure is:

A) An APPLICATION-LEVEL issue — the app container crashes because the app itself
   needs initialization (archivebox init, django migrate, etc.) or has a bad
   entrypoint. This is NOT a stacker bug. In this case:
   - Explain the root cause clearly (e.g. "ArchiveBox requires archivebox init before server start")
   - Suggest the fix in stacker.yml or the Dockerfile (e.g. add entrypoint.sh wrapper)
   - Do NOT search stacker source for this — return your diagnosis immediately.

B) A STACKER CLI bug — stacker itself crashes, generates wrong compose YAML,
   mishandles config, etc. In this case:
   1. Use grep_src to find relevant code (supports extended regex with |)
   2. Use read_file with line_offset/line_limit to paginate large files
      (the response header shows total lines — use line_offset to read past 150 lines)
   3. Identify the exact bug with file:line reference
   4. Write the Rust fix

Focus areas for stacker bugs:
- src/console/commands/cli/deploy.rs — deploy logic
- src/console/commands/cli/status.rs — status polling
- src/console/commands/cli/init.rs   — stacker.yml generation
- src/cli/config_parser.rs           — config parsing
- src/cli/generator/                 — compose/dockerfile generation

When writing a fix:
- Be surgical: change only what is needed
- Preserve existing error handling patterns
- Add no new dependencies
- Include a one-line comment only if the WHY is non-obvious
"""

SYSTEM_CLOUD_QA = """\
You are a QA Engineer verifying a remote cloud deployment managed by stacker.

Stacker has already provisioned a Hetzner server and deployed the app there.
You have the `run_shell` tool — all commands run locally, but stacker commands
(status, logs, etc.) communicate with the remote server transparently.

Run these checks in order:
1. `{stacker_cmd} status`
   → All containers must show "Up" (not "Restarting" or "Exited")
2. If a server IP is provided, attempt HTTP health checks:
   `curl -sf --connect-timeout 10 http://<ip>:<port>/health`
   `curl -sf --connect-timeout 10 http://<ip>:<port>/`  -o /dev/null -w "%{{http_code}}"
   (try port 80 first, then the app port)

Verdict:
- PASS: containers running AND at least one HTTP check returns 2xx/3xx
- PARTIAL: containers running but HTTP unreachable (firewall / not yet ready)
- FAIL: containers not running

Return your verdict as:
```
CLOUD QA VERDICT: PASS|PARTIAL|FAIL
Details: <brief explanation>
```
"""


# ── Tool handler factory ───────────────────────────────────────────────────────

def make_handler(
    *,
    github_token: Optional[str],
    project_dir: str,
    stacker_src: str,
):
    def handle(name: str, inputs: dict) -> str:
        # ── GitHub tools ───────────────────────────────────────
        if name == "search_github":
            lang = inputs["language"]
            min_stars = inputs.get("min_stars", 500)
            try:
                items = gh_search_repos(lang, github_token, min_stars)
                return json.dumps([
                    {
                        "full_name": r["full_name"],
                        "description": r.get("description", "")[:100],
                        "stars": r["stargazers_count"],
                        "language": r.get("language", ""),
                    }
                    for r in items[:8]
                ])
            except Exception as exc:
                return f"Error: {exc}"

        elif name == "check_repo_files":
            owner, repo = inputs["owner"], inputs["repo"]
            results = {}
            for p in inputs.get("paths", []):
                results[p] = gh_file_exists(owner, repo, p, github_token)
            return json.dumps(results)

        elif name == "read_github_file":
            content = gh_read_file(
                inputs["owner"], inputs["repo"], inputs["path"], github_token
            )
            return content[:8000] if content else "File not found"

        # ── File tools ─────────────────────────────────────────
        elif name == "write_file":
            path = inputs["path"]
            abs_project = os.path.abspath(project_dir)
            if os.path.isabs(path):
                abs_path = os.path.normpath(path)
            else:
                # Resolve from CWD first — the agent often prefixes the full
                # project-relative path (e.g. "stacker-projects/outline/stacker.yml")
                # when told the project directory. If that lands inside project_dir,
                # use it; otherwise resolve relative to project_dir as before.
                abs_cwd = os.path.abspath(os.getcwd())
                cwd_path = os.path.normpath(os.path.join(abs_cwd, path))
                if cwd_path.startswith(abs_project + os.sep) or cwd_path == abs_project:
                    abs_path = cwd_path
                else:
                    abs_path = os.path.normpath(os.path.join(abs_project, path))
            # Security: don't escape project_dir via ../
            if not abs_path.startswith(abs_project + os.sep) and abs_path != abs_project:
                abs_path = os.path.join(abs_project, os.path.basename(path))
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w") as f:
                f.write(inputs["content"])
            return f"Written {abs_path} ({len(inputs['content'])} bytes)"

        elif name == "read_file":
            path = inputs["path"]
            if not os.path.isabs(path):
                candidate = os.path.join(project_dir, path)
                if not os.path.exists(candidate):
                    candidate = os.path.join(stacker_src, path)
                path = candidate
            line_offset = int(inputs.get("line_offset", 0))
            line_limit = int(inputs.get("line_limit", 150))
            try:
                with open(path) as f:
                    lines = f.readlines()
                total = len(lines)
                chunk = "".join(lines[line_offset:line_offset + line_limit])
                header = f"[lines {line_offset+1}-{min(line_offset+line_limit, total)} of {total}]\n"
                return (header + chunk)[:8000]
            except Exception as exc:
                return f"Error reading {path}: {exc}"

        elif name == "grep_src":
            pattern = inputs["pattern"]
            directory = inputs.get("directory", "src/")
            if not os.path.isabs(directory):
                directory = os.path.join(stacker_src, directory)
            # -E enables extended regex so | alternation works
            rc, out = run_shell(f"grep -r -n -E {json.dumps(pattern)} {directory}", cwd=stacker_src)
            return out[:4000] or "No matches"

        # ── Shell tool ─────────────────────────────────────────
        elif name == "run_shell":
            cmd = inputs["command"]
            timeout = inputs.get("timeout", 180)
            rc, out = run_shell(cmd, cwd=project_dir, timeout=timeout)
            return f"[exit {rc}]\n{out}"

        return f"Unknown tool: {name}"

    return handle


# ── Repo finder (Python-driven, no model needed) ─────────────────────────────

# Dockerfile locations to probe, in preference order.
DOCKERFILE_LOCATIONS = [
    "Dockerfile",
    "docker/Dockerfile",
    "docker_example/Dockerfile",
    "deploy/Dockerfile",
    ".docker/Dockerfile",
    "build/Dockerfile",
]

COMPOSE_NAMES = ["docker-compose.yml", "docker-compose.yaml", "compose.yml"]

# Images that are infrastructure/support services, not the primary app image.
INFRA_IMAGE_PREFIXES = (
    "postgres",
    "mysql",
    "mariadb",
    "redis",
    "mongo",
    "rabbitmq",
    "memcached",
    "minio/",
    "bitnami/postgresql",
    "bitnami/mysql",
    "clickhouse/",
    "otel/",
    "opentelemetry/",
    "grafana/",
    "prom/",
    "prometheus",
    "nginx",
    "traefik",
    "caddy",
    "jc21/nginx-proxy-manager",
)

# Known upstream images for projects whose Dockerfile mostly wraps a public image.
# Keys are matched case-insensitively against repo/project names.
PUBLIC_IMAGE_HINTS = {
    "rustfs": "rustfs/rustfs:latest",
}


def _gh_check_dockerfile(
    owner: str, repo: str, token: Optional[str]
) -> tuple[Optional[str], Optional[str]]:
    """
    Probe common Dockerfile locations in owner/repo.
    Returns (dockerfile_path, compose_path_or_None), or (None, None) if no Dockerfile found.
    When a Dockerfile is found in a subdirectory, compose is searched in that same
    directory first before falling back to the repo root.
    Raises GitHubRateLimitError on 403 — caller must not record this repo as visited.
    """
    for df_path in DOCKERFILE_LOCATIONS:
        time.sleep(GH_DELAY)
        if not gh_file_exists(owner, repo, df_path, token):
            continue
        # Found a Dockerfile — look for compose in same dir first, then root
        df_dir = df_path.rsplit("/", 1)[0] if "/" in df_path else ""
        cp_candidates = (
            [f"{df_dir}/{cn}" for cn in COMPOSE_NAMES] + COMPOSE_NAMES
            if df_dir else COMPOSE_NAMES
        )
        seen: set[str] = set()
        for cp in cp_candidates:
            if cp in seen:
                continue
            seen.add(cp)
            time.sleep(GH_DELAY)
            if gh_file_exists(owner, repo, cp, token):
                return df_path, cp
        return df_path, None  # Dockerfile found, no compose
    return None, None  # no Dockerfile found anywhere


def find_deployable_repo(
    lang_key: str,
    token: Optional[str],
    skip: Optional[set] = None,
    checked: Optional[set] = None,
) -> Optional[dict]:
    """
    Find a repo that has a Dockerfile (required). docker-compose.yml is optional —
    the specialist can infer config from the Dockerfile and README alone.

    Order:
      1. Known-good repos (fast, verified, uses minimal requests)
      2. Top GitHub search results (broader, but burns more rate limit)

    Pass `skip` (a set of "owner/repo" strings) to exclude repos already checked.
    Pass `checked` (a mutable set) to collect every repo examined this run —
    the caller persists it so future runs skip them automatically.

    Returns a repo_info dict or None.
    """
    if skip is None:
        skip = set()

    # ── 1. Known-good repos first ──────────────────────────────
    print("  Checking known-good repos…")
    for entry in KNOWN_REPOS.get(lang_key, []):
        owner, repo = entry["owner"], entry["repo"]
        full_name = f"{owner}/{repo}"
        if full_name in skip:
            print(f"  ↷ {full_name} (already checked — skipping)")
            continue
        if checked is not None:
            checked.add(full_name)
        df_path, cp = _gh_check_dockerfile(owner, repo, token)
        if df_path:
            note = f"compose: {cp}" if cp else "Dockerfile only"
            print(f"  ✓ {owner}/{repo} (known-good, {note})")
            return {
                "owner": owner, "repo": repo,
                "full_name": full_name,
                "description": "(known-good)",
                "language": LANG_TO_GITHUB.get(lang_key, lang_key),
                "stars": 0,
                "dockerfile_path": df_path,
                "compose_path": cp,
            }
        print(f"  ✗ {owner}/{repo} (no Dockerfile)")

    # ── 2. Broad GitHub search (paginated) ────────────────────
    print("  Known-good repos unavailable — searching GitHub…")
    github_lang = LANG_TO_GITHUB.get(lang_key, lang_key)
    query = f"language:{github_lang} stars:>1000 fork:false"
    per_page = 10
    max_pages = 10  # up to 100 repos before giving up

    for page in range(1, max_pages + 1):
        params = {"q": query, "sort": "stars", "order": "desc",
                  "per_page": per_page, "page": page}
        candidates_list: list[dict] = []
        try:
            time.sleep(GH_DELAY)
            resp = requests.get(
                f"{GITHUB_API}/search/repositories",
                headers=_gh_headers(token),
                params=params,
                timeout=15,
            )
            if resp.status_code == 401 and token:
                print("  GitHub token rejected (401), retrying without auth…")
                time.sleep(GH_DELAY)
                resp = requests.get(
                    f"{GITHUB_API}/search/repositories",
                    headers=_gh_headers(None),
                    params=params,
                    timeout=15,
                )
            if resp.ok:
                candidates_list = resp.json().get("items", [])
        except GitHubRateLimitError as exc:
            print(f"  ✋ {exc}")
            break
        except Exception as exc:
            print(f"  GitHub search failed: {exc}")
            break

        if not candidates_list:
            break  # no more results

        all_skipped = True
        rate_limited = False
        for item in candidates_list:
            if item["full_name"] in skip:
                print(f"  ↷ {item['full_name']} (already checked — skipping)")
                continue
            all_skipped = False
            try:
                df_path, cp = _gh_check_dockerfile(
                    item["owner"]["login"], item["name"], token
                )
            except GitHubRateLimitError as exc:
                print(f"  ✋ {exc}")
                rate_limited = True
                break
            if checked is not None:
                checked.add(item["full_name"])
            if df_path:
                note = f"+compose ({cp})" if cp else f"Dockerfile only ({df_path})"
                print(f"  ✓ {item['full_name']} ({note})")
                return {
                    "owner": item["owner"]["login"], "repo": item["name"],
                    "full_name": item["full_name"],
                    "description": (item.get("description") or "")[:120],
                    "language": item.get("language", ""),
                    "stars": item["stargazers_count"],
                    "dockerfile_path": df_path,
                    "compose_path": cp,
                }
            print(f"  ✗ {item['full_name']} (no Dockerfile)")

        if rate_limited:
            break
        if all_skipped:
            print(f"  (page {page} fully skipped — fetching next page…)")

    return None


def _clean_image_ref(value: str) -> str:
    """Return a static Docker image ref, or empty when it is templated/invalid."""
    image = value.strip().strip("'\"")
    if not image or "$" in image or "{" in image or "}" in image:
        return ""
    return image


def _is_infra_image(image: str) -> bool:
    image = image.lower()
    image_no_registry = image.split("/", 1)[1] if "." in image.split("/", 1)[0] else image
    return any(
        image_no_registry == prefix or image_no_registry.startswith(prefix)
        for prefix in INFRA_IMAGE_PREFIXES
    )


def public_image_hint_for_repo(repo_info: dict, dockerfile_content: str, compose_content: Optional[str]) -> Optional[str]:
    """Find a public image that can replace a local Dockerfile build, when obvious."""
    names = {
        str(repo_info.get("repo", "")).lower(),
        str(repo_info.get("full_name", "")).rsplit("/", 1)[-1].lower(),
    }
    for name in names:
        if name in PUBLIC_IMAGE_HINTS:
            return PUBLIC_IMAGE_HINTS[name]

    compose_images: list[str] = []
    if compose_content:
        for match in re.finditer(r'^\s*image:\s*([^\s#]+)', compose_content, re.MULTILINE):
            image = _clean_image_ref(match.group(1))
            if image and not _is_infra_image(image):
                compose_images.append(image)

    if compose_images:
        repo_name = str(repo_info.get("repo", "")).lower().replace("_", "-")
        for image in compose_images:
            image_name = image.lower().split("/")[-1].split(":")[0]
            if repo_name in image_name or image_name in repo_name:
                return image
        if len(compose_images) == 1:
            return compose_images[0]

    from_match = re.search(r'^\s*FROM\s+([^\s]+)', dockerfile_content, re.MULTILINE | re.IGNORECASE)
    if from_match:
        base_image = _clean_image_ref(from_match.group(1).split(" AS ", 1)[0].split(" as ", 1)[0])
        repo_name = str(repo_info.get("repo", "")).lower().replace("_", "-")
        base_name = base_image.lower().split("/")[-1].split(":")[0]
        if base_image and repo_name and (repo_name in base_name or base_name in repo_name):
            return base_image

    return None


def prefer_public_image_in_stacker_yml(project_dir: str, image: Optional[str]) -> bool:
    """Replace app.dockerfile with app.image when a public app image is known."""
    if not image:
        return False
    stacker_yml = os.path.join(project_dir, "stacker.yml")
    try:
        content = open(stacker_yml).read()
    except FileNotFoundError:
        return False

    app_match = re.search(r'^app:\n(?P<body>(?:^[ \t]+.*\n?)*)', content, re.MULTILINE)
    if not app_match:
        return False
    app_body = app_match.group("body")
    if re.search(r'^[ \t]+image:\s*\S+', app_body, re.MULTILINE):
        return False
    if not re.search(r'^[ \t]+dockerfile:\s*\S+', app_body, re.MULTILINE):
        return False

    new_body = re.sub(
        r'^([ \t]+)dockerfile:\s*.*$',
        rf'\1image: {image}',
        app_body,
        count=1,
        flags=re.MULTILINE,
    )
    new_content = content[:app_match.start("body")] + new_body + content[app_match.end("body"):]
    with open(stacker_yml, "w") as f:
        f.write(new_content)
    return True


def has_build_only_app(project_dir: str) -> bool:
    stacker_yml = os.path.join(project_dir, "stacker.yml")
    try:
        content = open(stacker_yml).read()
    except FileNotFoundError:
        return False
    app_match = re.search(r'^app:\n(?P<body>(?:^[ \t]+.*\n?)*)', content, re.MULTILINE)
    if not app_match:
        return False
    app_body = app_match.group("body")
    return (
        re.search(r'^[ \t]+dockerfile:\s*\S+', app_body, re.MULTILINE) is not None
        and re.search(r'^[ \t]+image:\s*\S+', app_body, re.MULTILINE) is None
    )


# ── Stacker CLI detection ─────────────────────────────────────────────────────

def detect_stacker_cmd(binary: str, work_dir: str) -> str:
    """
    Return the correct base command prefix for stacker operations.

    Some builds ship as `stacker-cli` where commands are:
        stacker-cli stacker deploy

    Others ship as `stacker` where commands are:
        stacker deploy

    We probe `{binary} stacker --help` — if that exits 0 the binary expects
    the extra 'stacker' subcommand group; otherwise commands are direct.
    """
    rc, _ = run_shell(f"{binary} stacker --help", cwd=work_dir, timeout=5)
    if rc == 0:
        return f"{binary} stacker"
    return binary


# ── Orchestrator ───────────────────────────────────────────────────────────────

def parse_repo_json(text: str) -> Optional[dict]:
    """Extract JSON object from agent output."""
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        match = re.search(r'\{[^{}]*"owner"\s*:[^{}]*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env", default=".env", help="Path to .env / credentials file")
    parser.add_argument(
        "--lang", default="python",
        choices=["python", "nodejs", "typescript", "rust", "go"],
        help="Language for repo search (default: python)",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--work-dir", default=DEFAULT_WORK_DIR, help="Where project dirs are created")
    stacker_src_default = str(DEFAULT_STACKER_SRC) if DEFAULT_STACKER_SRC.exists() else "."
    parser.add_argument("--stacker-src", default=stacker_src_default, help="Stacker source root for Rust agent (default: auto-detected)")
    parser.add_argument("--repo", default=None, metavar="OWNER/REPO",
                        help="Skip Research Agent and use this repo directly (e.g. netbox-community/netbox)")
    parser.add_argument("--mcp", action="store_true",
                        help="Use Stacker MCP server for tools (requires websockets>=12.0)")
    parser.add_argument("--mcp-url", default=None,
                        help=f"Stacker MCP WebSocket URL (default: {DEFAULT_MCP_URL})")
    parser.add_argument("--anthropic", action="store_true",
                        help="Use Anthropic API instead of Ollama (reads ANTHROPIC_API_KEY)")
    parser.add_argument("--anthropic-model", default=None,
                        help="Claude model to use (default: claude-haiku-4-5-20251001)")
    parser.add_argument("--cloud", action="store_true",
                        help="After local QA, also deploy to Hetzner Cloud (reads HETZNER_TOKEN)")
    parser.add_argument("--cloud-region", default=None,
                        help=f"Hetzner datacenter region (default: {DEFAULT_CLOUD_REGION})")
    parser.add_argument("--cloud-size", default=None,
                        help=f"Hetzner server type (default: {DEFAULT_CLOUD_SIZE})")
    args = parser.parse_args()

    # ── Load credentials ───────────────────────────────────────
    env = load_env_file(args.env)
    ollama_host = env.get("OLLAMA_HOST") or os.environ.get("OLLAMA_HOST") or DEFAULT_OLLAMA_HOST
    ollama_model = env.get("OLLAMA_MODEL") or os.environ.get("OLLAMA_MODEL") or args.model
    github_token = env.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    github_token = validate_github_token(github_token)  # null out if invalid
    stacker_cli = env.get("STACKER_CLI") or os.environ.get("STACKER_CLI") or shutil.which("stacker-cli") or shutil.which("stacker") or "stacker"
    mcp_url = env.get("STACKER_MCP_URL") or os.environ.get("STACKER_MCP_URL") or args.mcp_url or DEFAULT_MCP_URL
    stacker_token = env.get("STACKER_TOKEN") or os.environ.get("STACKER_TOKEN") or read_stacker_token()
    ollama_api_key = env.get("OLLAMA_API_KEY") or os.environ.get("OLLAMA_API_KEY")
    anthropic_api_key = env.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    anthropic_model = (
        env.get("ANTHROPIC_MODEL") or os.environ.get("ANTHROPIC_MODEL") or
        args.anthropic_model or "claude-haiku-4-5-20251001"
    )
    use_anthropic = args.anthropic or bool(anthropic_api_key)
    hetzner_token = (
        env.get("HETZNER_TOKEN") or os.environ.get("HETZNER_TOKEN") or
        env.get("HCLOUD_TOKEN") or os.environ.get("HCLOUD_TOKEN")
    )
    cloud_region = env.get("CLOUD_REGION") or os.environ.get("CLOUD_REGION") or args.cloud_region or DEFAULT_CLOUD_REGION
    cloud_size   = env.get("CLOUD_SIZE")   or os.environ.get("CLOUD_SIZE")   or args.cloud_size   or DEFAULT_CLOUD_SIZE
    ssh_key_path = env.get("SSH_KEY_PATH") or os.environ.get("SSH_KEY_PATH") or DEFAULT_SSH_KEY_PATH
    run_cloud = args.cloud or bool(hetzner_token)

    if use_anthropic:
        if not anthropic_api_key:
            print("Error: --anthropic requires ANTHROPIC_API_KEY in .env or environment")
            return 1
        print(f"Anthropic API: model={anthropic_model}")
        _run = functools.partial(run_agent_anthropic,
                                 anthropic_model=anthropic_model,
                                 anthropic_api_key=anthropic_api_key)
    else:
        # Verify Ollama is reachable
        try:
            requests.get(f"{ollama_host}/api/tags", timeout=5).raise_for_status()
        except Exception as exc:
            print(f"Error: cannot reach Ollama at {ollama_host}: {exc}")
            return 1
        print(f"Ollama: {ollama_host}  model: {ollama_model}")
        if ollama_api_key:
            print(f"Ollama API key: {'*' * 8}{ollama_api_key[-4:]}")
        _run = functools.partial(run_agent,
                                 ollama_host=ollama_host,
                                 ollama_model=ollama_model,
                                 ollama_api_key=ollama_api_key)

    print(f"stacker binary: {stacker_cli}")
    os.makedirs(args.work_dir, exist_ok=True)

    # Load already-deployed repos (successes) and previously-checked repos (no Docker files found).
    # Both are skipped during repo search to avoid re-checking the same repos every run.
    deployed_log = os.path.join(args.work_dir, ".deployed")
    visited_log  = os.path.join(args.work_dir, ".visited")
    deployed: set[str] = set()
    visited: set[str] = set()
    if os.path.exists(deployed_log):
        with open(deployed_log) as f:
            deployed = {line.strip() for line in f if line.strip()}
    if os.path.exists(visited_log):
        with open(visited_log) as f:
            visited = {line.strip() for line in f if line.strip()}
    if deployed:
        print(f"  Skipping {len(deployed)} already-deployed repo(s): {', '.join(sorted(deployed))}")
    if visited:
        print(f"  Skipping {len(visited)} previously-checked repo(s) with no Docker files")

    stacker_cmd = detect_stacker_cmd(stacker_cli, args.work_dir)
    print(f"stacker command prefix: {stacker_cmd}")

    github_lang = LANG_TO_GITHUB[args.lang]

    # ── Phase 1: Find repo ────────────────────────────────────
    print("\n[Phase 1/4] Finding deployable repo…")
    if args.repo:
        parts = args.repo.split("/", 1)
        if len(parts) != 2:
            print("Error: --repo must be in OWNER/REPO format")
            return 1
        owner_arg, repo_arg = parts
        # Probe for Dockerfile location and optional compose
        try:
            _df, _cp = _gh_check_dockerfile(owner_arg, repo_arg, github_token)
        except Exception:
            _df, _cp = "Dockerfile", None
        repo_info: dict = {
            "owner": owner_arg, "repo": repo_arg,
            "full_name": args.repo, "description": "(manual override)",
            "language": github_lang, "stars": 0,
            "dockerfile_path": _df or "Dockerfile", "compose_path": _cp,
        }
        print(f"  Using --repo override: {args.repo}")
    else:
        print(f"  Searching GitHub for {github_lang} web apps with a Dockerfile…")
        newly_checked: set[str] = set()
        repo_info = find_deployable_repo(
            args.lang, github_token,
            skip=deployed | visited,
            checked=newly_checked,
        )
        # Persist every repo checked this run so future runs skip them.
        new_to_save = newly_checked - visited - deployed
        if new_to_save:
            with open(visited_log, "a") as f:
                for r in sorted(new_to_save):
                    f.write(f"{r}\n")
        if not repo_info:
            print("\nCould not find a suitable repo automatically.")
            print("Specify one manually with --repo, e.g.:")
            for entry in KNOWN_REPOS.get(args.lang, []):
                print(f"  --repo {entry['owner']}/{entry['repo']}")
            return 1

    # ── Pre-fetch Docker files ─────────────────────────────────
    owner, repo_name = repo_info["owner"], repo_info["repo"]
    compose_path = repo_info.get("compose_path")
    print(f"\n  ✓ {repo_info['full_name']} ({repo_info.get('stars', '?')} ★) — {repo_info.get('description', '')}")
    print(f"  Fetching Dockerfile" + (f" and {compose_path}" if compose_path else "") + "…")

    dockerfile_content = gh_read_file(owner, repo_name, repo_info.get("dockerfile_path", "Dockerfile"), github_token)
    compose_content = gh_read_file(owner, repo_name, compose_path, github_token) if compose_path else None

    if not dockerfile_content:
        print("  Dockerfile: ✗  — cannot proceed without it.")
        print("Specify a different repo with --repo.")
        return 1

    print(f"  Dockerfile: {len(dockerfile_content)} bytes" +
          (f"  compose: {len(compose_content)} bytes" if compose_content else "  compose: not found (will infer from Dockerfile + README)"))

    public_image_hint = public_image_hint_for_repo(repo_info, dockerfile_content, compose_content)
    if public_image_hint:
        print(f"  Public app image candidate: {public_image_hint}")

    # Pre-fetch README for deployment hints (TLS flags, required env vars, local dev notes)
    readme_content = (
        gh_read_file(owner, repo_name, "README.md", github_token) or
        gh_read_file(owner, repo_name, "readme.md", github_token) or
        gh_read_file(owner, repo_name, "README", github_token) or
        ""
    )
    if readme_content:
        print(f"  README: {len(readme_content)} bytes")

    # ── Create project directory ───────────────────────────────
    project_dir = os.path.join(args.work_dir, repo_name)
    os.makedirs(project_dir, exist_ok=True)

    # Ensure the work-dir gitignores .env files so project-specific vars
    # (DB passwords, admin creds) never leak into version control.
    gitignore_path = os.path.join(args.work_dir, ".gitignore")
    gitignore_line = "**/.env\n"
    try:
        existing = open(gitignore_path).read() if os.path.exists(gitignore_path) else ""
        if "**/.env" not in existing:
            with open(gitignore_path, "a") as f:
                f.write(gitignore_line)
    except OSError:
        pass

    # Create a fresh, empty project .env for app-specific vars (DB passwords,
    # ports, etc.). The main .env stays in the top-level directory and is
    # never copied here — it contains tokens that should not be in project dirs.
    project_env = os.path.join(project_dir, ".env")
    if not os.path.exists(project_env):
        open(project_env, "w").close()
    print(f"Project .env: {project_env} (Specialist will add app-specific vars)")

    # ── MCP setup (optional) ───────────────────────────────────
    mcp_client: Optional[StackerMcpClient] = None
    mcp_ctx = None

    if args.mcp:
        if not stacker_token:
            print("Error: --mcp requires a Stacker Bearer token.")
            print("Run `stacker login` first, or set STACKER_TOKEN in .env")
            return 1
        print(f"\nConnecting to Stacker MCP at {mcp_url}…")
        mcp_client = StackerMcpClient(mcp_url, stacker_token)
        mcp_ctx = mcp_client.__enter__()

    handler = (
        mcp_ctx.make_handler(
            project_dir=project_dir,
            stacker_src=args.stacker_src,
            github_token=github_token,
        )
        if mcp_ctx else
        make_handler(
            github_token=github_token,
            project_dir=project_dir,
            stacker_src=args.stacker_src,
        )
    )

    # Tools for the Specialist: curated MCP subset + local file/shell tools, or just local.
    # We deliberately limit MCP tools to ~7 relevant ones — sending all 100+ at once
    # produces a request too large for most proxy/model setups.
    if mcp_ctx:
        mcp_specialist = mcp_ctx.as_ollama_tools(only=MCP_TOOLS_SPECIALIST)
        specialist_tools = mcp_specialist + TOOLS_SPECIALIST
        print(f"  Specialist has {len(specialist_tools)} tools "
              f"({len(mcp_specialist)} MCP + {len(TOOLS_SPECIALIST)} local)")
    else:
        specialist_tools = TOOLS_SPECIALIST

    # ── Phase 2: Stacker Specialist ────────────────────────────
    print("\n[Phase 2/4] Stacker Specialist — generating stacker.yml and deploying…")
    deploy_result = _run(
        label="Stacker Specialist",
        system=SYSTEM_SPECIALIST,
        user_msg=(
            f"Deploy {repo_info['full_name']} locally.\n\n"
            f"Repo details: {json.dumps(repo_info, indent=2)}\n\n"
            f"Project directory: {project_dir}\n"
            f"App .env: {project_dir}/.env  ← write app-specific vars here only (DB passwords, ports, "
            f"admin credentials). Do NOT write API keys or auth tokens.\n\n"
            + (
                f"PUBLIC IMAGE POLICY:\n"
                f"- A public app image appears to be available: {public_image_hint}\n"
                f"- Use `app.image: {public_image_hint}` instead of `app.dockerfile` unless the Dockerfile is required for custom app code.\n"
                f"- This matters for cloud deploys: Stacker can pull public images remotely, but it does not push local Dockerfile builds to a registry.\n\n"
                if public_image_hint else
                f"PUBLIC IMAGE POLICY:\n"
                f"- If the compose file contains a public image for the main app, use `app.image` instead of `app.dockerfile`.\n"
                f"- If no public app image exists, `app.dockerfile` is acceptable for local deploy only; cloud deploy requires CI/CD to publish that image first.\n\n"
            )
            + f"The Docker files have already been fetched — do NOT call read_github_file:\n\n"
            f"=== {repo_info.get('dockerfile_path', 'Dockerfile')} ===\n"
            f"{dockerfile_content[:3000]}\n\n"
            + (
                f"=== {compose_path} ===\n"
                f"{compose_content[:3000]}\n\n"
                if compose_content else
                f"=== docker-compose.yml ===\n"
                f"(not present in repo — infer ports, volumes, and environment from the Dockerfile,\n"
                f" README, and any `docker run` examples shown there)\n\n"
            )
            + (
                f"=== README.md (first 2000 chars — read for TLS flags, required env vars, local dev notes) ===\n"
                f"{readme_content[:2000]}\n\n"
                if readme_content else ""
            )
            + f"IMPORTANT — use EXACTLY these commands (no other variations):\n"
            f"  dry-run : {stacker_cmd} deploy --target local --dry-run\n"
            f"  deploy  : {stacker_cmd} deploy --target local\n"
            f"  status  : {stacker_cmd} status\n"
            f"  pipe scan: {stacker_cmd} pipe scan --json\n"
            f"  pipe create: {stacker_cmd} pipe create <source-app-code> <target-app-code>\n\n"
            + (
                f"You also have access to Stacker MCP tools (70+ available). Useful ones:\n"
                f"  validate_stack_config — validate stacker.yml before deploying\n"
                f"  recommend_stack_services — get service recommendations for this app type\n"
                f"  discover_stack_services — parse compose to discover service structure\n"
                f"  list_pipe_templates — see available pipe connection patterns\n\n"
                if mcp_ctx else ""
            )
            + f"Write stacker.yml using ONLY the bare filename 'stacker.yml' (no path prefix).\n"
            f"CRITICAL: write_file content must be real valid YAML — never use placeholders like "
            f"'<stacker.yml content here>'.\n\n"
            f"Steps:\n"
            f"1. Identify all services from the compose file above\n"
            f"2. Write stacker.yml\n"
            f"3. Dry-run to validate, then deploy\n"
            f"4. Poll status every 30s up to 5 times until running\n"
            f"5. Run pipe scan to discover app codes, then pipe create IF there are at least 2 services\n"
            f"   (skip pipe create if there is only one service — nothing to connect)\n"
            f"6. Write README.md to the project directory. Keep it compact — max 40 lines. Include:\n"
            f"   - One-line description of what the app does\n"
            f"   - .env variables the user must set before deploying\n"
            f"   - Deploy command: `stacker deploy --target local`\n"
            f"   - Access URLs (ports from stacker.yml)\n"
            f"   - Status/logs: `stacker status` and `stacker logs`\n"
            f"   - Stop: `docker compose -f .stacker/docker-compose.yml down`\n"
            f"   - Any app-specific notes (default credentials, init steps, etc.)\n"
        ),
        tools=specialist_tools,
        tool_fn=handler,
        max_turns=25,
    )

    # Guard: verify stacker.yml was actually written with real content
    stacker_yml_path = os.path.join(project_dir, "stacker.yml")
    if os.path.exists(stacker_yml_path):
        with open(stacker_yml_path) as f:
            yml_content = f.read()
        if "<" in yml_content and ">" in yml_content:
            print("\nWarning: stacker.yml contains placeholder content — the model did not generate real YAML.")
            print("Run with --repo OWNER/REPO and a model that supports tool use well (e.g. --model qwen2.5:14b)")
    else:
        print("\nWarning: stacker.yml was not written by the Specialist.")

    public_image_rewrite_applied = prefer_public_image_in_stacker_yml(project_dir, public_image_hint)
    if public_image_rewrite_applied:
        print(f"  Updated stacker.yml: using public app image {public_image_hint} instead of a local Dockerfile build")
        print("  Note: run deploy with --force-rebuild to regenerate .stacker/docker-compose.yml from this change.")

    # ── Phase 3: QA ────────────────────────────────────────────
    print("\n[Phase 3/4] QA Tester — verifying deployment health…")
    compose_path = os.path.abspath(os.path.join(project_dir, ".stacker", "docker-compose.yml"))
    if mcp_ctx:
        mcp_qa = mcp_ctx.as_ollama_tools(only=MCP_TOOLS_QA)
        qa_tools = mcp_qa + TOOLS_QA
    else:
        qa_tools = TOOLS_QA
    qa_result = _run(
        label="QA Tester",
        system=SYSTEM_QA,
        user_msg=(
            f"Verify the {repo_name} deployment.\n\n"
            f"Use this EXACT compose file path (do not modify it):\n"
            f"  {compose_path}\n\n"
            f"Commands to run:\n"
            f"  docker compose -f {compose_path} ps\n"
            f"  docker compose -f {compose_path} logs --tail=100\n\n"
            f"Return QA VERDICT: PASS or FAIL."
        ),
        tools=qa_tools,
        tool_fn=handler,
    )

    qa_passed = "QA VERDICT: PASS" in qa_result

    # Close MCP connection — no longer needed after QA
    if mcp_ctx:
        mcp_client.__exit__(None, None, None)
        mcp_ctx = None

    # ── Phase 4: Rust Developer (only on failure) ──────────────
    rust_report = ""
    if not qa_passed:
        print("\n[Phase 4/4] Rust Developer — analyzing stacker CLI issues…")
        stacker_yml_content = ""
        try:
            with open(os.path.join(project_dir, "stacker.yml")) as f:
                stacker_yml_content = f.read()
        except FileNotFoundError:
            pass

        rust_report = _run(
            label="Rust Developer",
            system=SYSTEM_RUST_DEV,
            user_msg=(
                f"The {repo_name} deployment failed QA.\n\n"
                f"QA report:\n{qa_result}\n\n"
                f"Deploy output (last part):\n{deploy_result[-1500:]}\n\n"
                f"stacker.yml used:\n{stacker_yml_content}\n\n"
                f"Stacker source root: {args.stacker_src}\n\n"
                f"Analyze what went wrong in the stacker CLI and provide a fix."
            ),
            tools=TOOLS_RUST_DEV,
            tool_fn=make_handler(
                github_token=github_token,
                project_dir=project_dir,
                stacker_src=args.stacker_src,
            ),
        )
        print(f"\nRust Developer Report:\n{rust_report}")
    else:
        print("\n[Phase 4/4] Rust Developer — skipped (QA passed)")

    # ── Phase 5: Cloud deploy (Hetzner) — only when local QA passed ────────────
    cloud_qa_passed: Optional[bool] = None
    if run_cloud and qa_passed:
        if not hetzner_token:
            print("\n[Phase 5] Cloud Deploy — skipped (no HETZNER_TOKEN)")
        elif has_build_only_app(project_dir):
            print("\n[Phase 5] Cloud Deploy — skipped (build-only app)")
            print("  stacker.yml uses app.dockerfile without app.image.")
            print("  Local deploy can build that image, but remote cloud deploys need a registry image.")
            print("  Publish the image from CI/CD, then set app.image to the registry tag and retry cloud deploy.")
            cloud_qa_passed = False
        else:
            print(f"\n[Phase 5] Cloud Deploy — Hetzner {cloud_region}/{cloud_size}…")
            # Inject cloud: section into stacker.yml (keeps target: local for the
            # local path; --target cloud overrides it on the command line).
            if not add_cloud_config_to_stacker_yml(project_dir, cloud_region, cloud_size, ssh_key_path):
                print("  Warning: stacker.yml not found — skipping cloud deploy")
            else:
                print(f"  Updated stacker.yml with cloud provider=hetzner region={cloud_region} size={cloud_size}")

                # Expose token to all child processes (stacker reads HCLOUD_TOKEN).
                cloud_env = {**os.environ, "HCLOUD_TOKEN": hetzner_token}

                force_arg = " --force-rebuild" if public_image_rewrite_applied else ""
                print(f"  Running: stacker deploy --target cloud --lock{force_arg}  (may take a few minutes)")
                rc, deploy_out = run_shell(
                    f"{stacker_cmd} deploy --target cloud --lock{force_arg}",
                    cwd=project_dir, timeout=600, env=cloud_env,
                )
                print(deploy_out[:2000] + ("…" if len(deploy_out) > 2000 else ""))

                if rc != 0:
                    print("  Cloud deploy failed (see output above).")
                    cloud_qa_passed = False
                else:
                    server_ip = get_cloud_server_ip(project_dir, stacker_cmd)
                    ip_note = f"Server IP: {server_ip}" if server_ip else "Server IP: unknown (check stacker status)"
                    print(f"  {ip_note}")

                    # Temporarily set HCLOUD_TOKEN so stacker commands inside the
                    # agent (via run_shell → subprocess) can reach the cloud server.
                    os.environ["HCLOUD_TOKEN"] = hetzner_token

                    cloud_qa_result = _run(
                        label="Cloud QA",
                        system=SYSTEM_CLOUD_QA.format(stacker_cmd=stacker_cmd),
                        user_msg=(
                            f"Verify the cloud deployment of {repo_name} on Hetzner.\n\n"
                            f"{ip_note}\n"
                            f"App port: 8000\n"
                            f"Project directory: {project_dir}\n\n"
                            f"Run `{stacker_cmd} status` to confirm containers are up, "
                            f"then HTTP-check the server IP."
                        ),
                        tools=TOOLS_QA,
                        tool_fn=handler,
                    )
                    cloud_qa_passed = "CLOUD QA VERDICT: PASS" in cloud_qa_result

    elif run_cloud and not qa_passed:
        print("\n[Phase 5] Cloud Deploy — skipped (local QA did not pass)")

    # ── Summary ────────────────────────────────────────────────
    local_status = "PASS" if qa_passed else "FAIL"
    cloud_status = ("PASS" if cloud_qa_passed else "FAIL") if cloud_qa_passed is not None else "skipped"
    overall_ok = qa_passed and (cloud_qa_passed is not False)
    notify("Stacker AutoDeploy", f"{repo_name} — local:{local_status} cloud:{cloud_status}")

    # Record successful deployments so future auto-discovery runs skip them.
    if qa_passed and not args.repo:
        full_name = repo_info["full_name"]
        if full_name not in deployed:
            with open(deployed_log, "a") as f:
                f.write(f"{full_name}\n")
            print(f"  Recorded {full_name} in {deployed_log}")

    print(f"\n{'═'*62}")
    print(f"  Repo        : {repo_info['full_name']}")
    print(f"  Project dir : {project_dir}")
    print(f"  Local QA    : {local_status}")
    print(f"  Cloud QA    : {cloud_status}")
    if not qa_passed and rust_report:
        print(f"  Rust fix    : see Rust Developer output above")
    print(f"{'═'*62}\n")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
