#!/bin/sh
# Test claim-org.sh against a stub PipesHub API: needs sh, curl, python3.
set -eu
cd "$(dirname "$0")"
work=$(mktemp -d)
trap 'kill "$stub" 2>/dev/null || true; rm -rf "$work"' EXIT

cat >"$work/stub.py" <<'PY'
import json, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
state = {"exists": os.environ.get("ORG_EXISTS") == "1", "health_calls": 0}
log = sys.argv[1]
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def reply(self, code, obj):
        body = json.dumps(obj, separators=(",", ":")).encode()  # compact, like PipesHub
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == "/api/v1/health/services":
            state["health_calls"] += 1
            ok = state["health_calls"] > 1   # unhealthy on the first poll
            return self.reply(200 if ok else 503, {"status": "healthy" if ok else "starting"})
        if self.path == "/api/v1/org/exists":
            return self.reply(200, {"exists": state["exists"]})
        self.reply(404, {})
    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with open(log, "a") as f: f.write(json.dumps(data) + "\n")
        state["exists"] = True
        self.reply(200, {"ok": True})
srv = HTTPServer(("127.0.0.1", 0), H)
print(srv.server_address[1], flush=True)
srv.serve_forever()
PY

start_stub() {
  : >"$work/posts"
  ORG_EXISTS="$1" python3 "$work/stub.py" "$work/posts" >"$work/port" &
  stub=$!
  while [ ! -s "$work/port" ]; do sleep 0.1; done
  export PIPESHUB_API="http://127.0.0.1:$(cat "$work/port")/api/v1"
}
fail() { echo "FAIL: $1" >&2; exit 1; }
export PIPESHUB_WAIT_SECONDS=0 ADMIN_EMAIL='owner@example.com' ADMIN_PASSWORD='Pa"ss\word-1A'

# Fresh instance: waits for health, then creates exactly one org with the form login.
start_stub 0
./claim-org.sh >/dev/null || fail "claim on a fresh instance exited non-zero"
[ "$(wc -l <"$work/posts" | tr -d ' ')" = 1 ] || fail "expected one POST /org"
python3 - "$work/posts" <<'PY' || fail "org payload is wrong"
import json, sys
d = json.loads(open(sys.argv[1]).readline())
assert d == {"accountType": "individual", "contactEmail": "owner@example.com",
             "adminFullName": "Admin", "password": 'Pa"ss\\word-1A'}, d
PY
kill "$stub"; wait "$stub" 2>/dev/null || true; rm -f "$work/port"

# Existing organization: a reboot must not try to create another one.
start_stub 1
./claim-org.sh >/dev/null || fail "claim on a claimed instance exited non-zero"
[ ! -s "$work/posts" ] || fail "POST /org sent although an org exists"
kill "$stub"; wait "$stub" 2>/dev/null || true; rm -f "$work/port"

# Never healthy: gives up with an error instead of looping forever.
PIPESHUB_API="http://127.0.0.1:9/api/v1" PIPESHUB_WAIT_TRIES=2 ./claim-org.sh 2>/dev/null \
  && fail "claim succeeded although PipesHub never came up"

# A password PipesHub would refuse fails before any request, with the rule named.
start_stub 0
out=$(ADMIN_PASSWORD='alllowercase12' ./claim-org.sh 2>&1) && fail "weak password accepted"
echo "$out" | grep -q 'uppercase' || fail "weak password error does not name the rule"
[ ! -s "$work/posts" ] || fail "POST /org sent with a weak password"
kill "$stub"; wait "$stub" 2>/dev/null || true; rm -f "$work/port"

echo "claim-org: all tests passed"
