#!/bin/sh
# Test n8n-entrypoint.sh against the real n8n image (SQLite, no Postgres).
# Needs docker and curl.
set -eu
cd "$(dirname "$0")"
IMAGE=$(sed -n 's/^ *image: \(n8nio\/n8n:.*\)$/\1/p' ../stacker.yml)
# A deploy uploads the script without its executable bit: test it that way.
script=$(mktemp); cp n8n-entrypoint.sh "$script"; chmod 644 "$script"
run() { docker run --entrypoint tini -v "$script:/n8n-entrypoint.sh:ro" "$@"; }
name=n8n-entrypoint-test-$$
port=${TEST_PORT:-15678}
email=owner@example.com
password=GeneratedPassw0rdx
trap 'docker rm -f "$name" >/dev/null 2>&1 || true; rm -f "$script"' EXIT
fail() { echo "FAIL: $1" >&2; docker logs "$name" 2>&1 | tail -20 >&2; exit 1; }

# The template starts the script through sh, so it does not need the bit.
grep -q '^    entrypoint: "tini -- sh /n8n-entrypoint.sh"$' ../stacker.yml \
  || fail "stacker.yml does not start n8n through sh /n8n-entrypoint.sh"

# Without the login it refuses to start.
if run --rm "$IMAGE" -- sh /n8n-entrypoint.sh >/dev/null 2>&1; then
  fail "started without ADMIN_EMAIL / ADMIN_PASSWORD"
fi

run -d --name "$name" -p "127.0.0.1:$port:5678" \
  -e ADMIN_EMAIL="$email" -e ADMIN_PASSWORD="$password" -e N8N_SECURE_COOKIE=false \
  "$IMAGE" -- sh /n8n-entrypoint.sh >/dev/null

tries=0
until curl -sf "http://127.0.0.1:$port/healthz/readiness" >/dev/null; do
  tries=$((tries + 1)); [ "$tries" -lt 90 ] || fail "n8n did not start"; sleep 2
done

# The owner exists before anyone opens the UI: no setup screen.
curl -sf "http://127.0.0.1:$port/rest/settings" | grep -q '"showSetupOnFirstLoad":false' \
  || fail "n8n still offers owner setup"

login() {
  curl -s -o /dev/null -w '%{http_code}' -H 'Content-Type: application/json' \
    -d "{\"emailOrLdapLoginId\":\"$email\",\"password\":\"$1\"}" "http://127.0.0.1:$port/rest/login"
}
[ "$(login "$password")" = 200 ] || fail "owner cannot log in with ADMIN_PASSWORD"
[ "$(login wrong-Passw0rd)" = 401 ] || fail "a wrong password is accepted"

# The plain password does not reach n8n's own environment.
# (the n8n process is the only child of tini, PID 1)
docker exec "$name" sh -c 'cat /proc/$(pgrep -P 1 | head -1)/environ | tr "\0" "\n"' \
  | grep -q '^ADMIN_PASSWORD=' && fail "ADMIN_PASSWORD is visible to the n8n process"

echo "n8n-entrypoint: all tests passed"
