#!/bin/bash

# Ensure Plausible's backing services are ready and the ClickHouse database
# exists before we let the app retry its startup sequence.
set -euo pipefail

readonly APP_SERVICE="app"
readonly CLICKHOUSE_DATABASE="plausible"
readonly CLICKHOUSE_SERVICE="plausible_events_db"
readonly POSTGRES_DATABASE="plausible"
readonly POSTGRES_SERVICE="plausible_db"
readonly RETRY_DELAY_SECONDS=2
readonly RETRY_LIMIT=30

log() {
  echo "[plausible-post-deploy] $*"
}

find_container() {
  local service_name="${1}"

  docker ps -aq --filter "label=my.stacker.service=${service_name}" --latest
}

find_running_container() {
  local service_name="${1}"

  docker ps -q --filter "label=my.stacker.service=${service_name}" --latest
}

exec_in_container() {
  local service_name="${1}"
  shift

  local container_id
  container_id="$(find_running_container "${service_name}")"

  if [[ -z "${container_id}" ]]; then
    echo "Error: could not find container for service '${service_name}'" >&2
    return 1
  fi

  docker exec "${container_id}" "$@"
}

wait_for_postgres() {
  local attempt

  for attempt in $(seq 1 "${RETRY_LIMIT}"); do
    if exec_in_container "${POSTGRES_SERVICE}" pg_isready -U postgres -d "${POSTGRES_DATABASE}" >/dev/null 2>&1; then
      log "Postgres is ready"
      return 0
    fi

    sleep "${RETRY_DELAY_SECONDS}"
  done

  echo "Error: Postgres did not become ready in time" >&2
  return 1
}

wait_for_clickhouse() {
  local attempt

  for attempt in $(seq 1 "${RETRY_LIMIT}"); do
    if exec_in_container "${CLICKHOUSE_SERVICE}" clickhouse-client --query "SELECT 1" >/dev/null 2>&1; then
      log "ClickHouse is ready"
      return 0
    fi

    sleep "${RETRY_DELAY_SECONDS}"
  done

  echo "Error: ClickHouse did not become ready in time" >&2
  return 1
}

ensure_clickhouse_database() {
  log "Ensuring ClickHouse database '${CLICKHOUSE_DATABASE}' exists"
  exec_in_container \
    "${CLICKHOUSE_SERVICE}" \
    clickhouse-client \
    --query "CREATE DATABASE IF NOT EXISTS ${CLICKHOUSE_DATABASE}"
}

restart_app() {
  local app_container
  app_container="$(find_container "${APP_SERVICE}")"

  if [[ -z "${app_container}" ]]; then
    echo "Error: could not find app container to restart" >&2
    return 1
  fi

  log "Restarting Plausible app container"
  docker restart "${app_container}" >/dev/null
}

main() {
  wait_for_postgres
  wait_for_clickhouse
  ensure_clickhouse_database
  restart_app
  log "Post-deploy bootstrap complete"
}

main "$@"
