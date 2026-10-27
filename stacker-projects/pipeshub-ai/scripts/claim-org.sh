#!/bin/sh
# Create the first PipesHub organization with the admin login from the deploy
# form. PipesHub's POST /api/v1/org is unauthenticated and whoever reaches a
# fresh instance first owns it, so a public server must not wait for a browser.
# Runs on every boot and does nothing once an organization exists.
set -eu

API="${PIPESHUB_API:-http://app:3000/api/v1}"
: "${ADMIN_EMAIL:?ADMIN_EMAIL is not set}"
: "${ADMIN_PASSWORD:?ADMIN_PASSWORD is not set}"

# PipesHub's own password rule; checked here because a contract pattern
# cannot express "contains each of".
for class in '[A-Z]' '[a-z]' '[0-9]' '[#?!@$%^&*-]'; do
  if ! printf '%s' "$ADMIN_PASSWORD" | grep -q -- "$class"; then
    echo "claim-org: ADMIN_PASSWORD needs 8+ characters with an uppercase letter," \
      "a lowercase letter, a number and one of #?!@\$%^&*-" >&2
    exit 1
  fi
done

tries=0
until curl -sf "$API/health/services" | grep -q 'status.:.healthy'; do
  tries=$((tries + 1))
  if [ "$tries" -ge "${PIPESHUB_WAIT_TRIES:-180}" ]; then
    echo "claim-org: PipesHub did not become healthy, giving up" >&2
    exit 1
  fi
  sleep "${PIPESHUB_WAIT_SECONDS:-10}"
done

if curl -sf "$API/org/exists" | grep -Eq '"exists": ?true'; then
  echo "claim-org: organization already exists"
  exit 0
fi

esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }
body=$(printf '{"accountType":"individual","contactEmail":"%s","adminFullName":"Admin","password":"%s"}' \
  "$(esc "$ADMIN_EMAIL")" "$(esc "$ADMIN_PASSWORD")")

code=$(printf '%s' "$body" | curl -s -o /tmp/claim-org.out -w '%{http_code}' \
  -H 'Content-Type: application/json' --data-binary @- "$API/org")
case "$code" in
  2??) echo "claim-org: organization created for $ADMIN_EMAIL" ;;
  *)
    echo "claim-org: POST /org returned $code: $(head -c 300 /tmp/claim-org.out)" >&2
    exit 1
    ;;
esac
