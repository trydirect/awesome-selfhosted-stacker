#!/bin/bash

# Deploy Plausible through Stacker's agent deploy-app config bundle path.
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly APP_CODE="plausible"
readonly ENVIRONMENT="production"
readonly COMPOSE_SOURCE="${PROJECT_DIR}/docker/production/compose.yml"
readonly ENV_SOURCE="${PROJECT_DIR}/.env"
readonly INIT_SQL_SOURCE="${PROJECT_DIR}/.deploy-config/init-clickhouse.sql"

CLOUD_KEY="${STACKER_CLOUD_KEY:-htz-0}"
DEPLOYMENT_HASH="${STACKER_DEPLOYMENT_HASH:-}"
APPLY_PLAN=""
FORCE_APP=true
FORCE_NEW=false
PLAN_ONLY=false
RUN_STACKER_DEPLOY=false

usage() {
  cat <<USAGE
Usage: scripts/deploy-cloud.sh [OPTIONS]

Options:
  --key NAME              Stacker cloud key to use when provisioning (default: htz-0)
  --provision             Run stacker deploy before agent app deployment
  --force-new             Pass --force-new to stacker deploy; implies --provision
  --deployment HASH       Target a specific Stacker deployment hash
  --plan                  Print a read-only agent deploy-app plan
  --apply-plan HASH       Revalidate and apply a deploy-app plan fingerprint
  --no-force-app          Do not pass --force to agent deploy-app
  -h, --help              Show this help
USAGE
}

log() {
  echo "[plausible-deploy] $*"
}

fail() {
  echo "Error: $*" >&2
  exit 1
}

require_file() {
  local path="${1}"
  local label="${2}"

  [[ -f "${path}" ]] || fail "${label} not found: ${path}"
}

run_stacker_deploy() {
  local args=(deploy --target=cloud "--key=${CLOUD_KEY}")

  if [[ "${FORCE_NEW}" == true ]]; then
    args+=(--force-new)
  fi

  log "Provisioning/updating cloud server with Stacker"
  (cd "${PROJECT_DIR}" && stacker "${args[@]}")
}

patch_base_url() {
  local lock_file="${PROJECT_DIR}/.stacker/deployment-cloud.lock"

  if [[ ! -f "${lock_file}" ]]; then
    log "Warning: deployment lock not found — skipping BASE_URL patch"
    return 0
  fi

  local server_ip
  server_ip="$(grep '^server_ip:' "${lock_file}" | awk '{print $2}')"

  if [[ -z "${server_ip}" || "${server_ip}" == "null" ]]; then
    log "Warning: no server IP in deployment lock — skipping BASE_URL patch"
    return 0
  fi

  local new_base_url="http://${server_ip}:8000"
  local current_base_url
  current_base_url="$(grep '^BASE_URL=' "${ENV_SOURCE}" | cut -d= -f2-)"

  if [[ "${current_base_url}" == "${new_base_url}" ]]; then
    log "BASE_URL already set to ${new_base_url}"
    return 0
  fi

  log "Updating BASE_URL to ${new_base_url} (was: ${current_base_url})"
  local tmp
  tmp="$(mktemp)"
  sed "s|^BASE_URL=.*|BASE_URL=${new_base_url}|" "${ENV_SOURCE}" > "${tmp}"
  mv "${tmp}" "${ENV_SOURCE}"
}

run_agent_deploy_app() {
  local args=(agent deploy-app "${APP_CODE}" --env "${ENVIRONMENT}")

  if [[ "${FORCE_APP}" == true ]]; then
    args+=(--force)
  fi

  if [[ -n "${DEPLOYMENT_HASH}" ]]; then
    args+=(--deployment "${DEPLOYMENT_HASH}")
  fi

  if [[ "${PLAN_ONLY}" == true ]]; then
    args+=(--plan)
  fi

  if [[ -n "${APPLY_PLAN}" ]]; then
    args+=(--apply-plan "${APPLY_PLAN}")
  fi

  log "Deploying Plausible with Stacker agent config bundle"
  (cd "${PROJECT_DIR}" && stacker "${args[@]}")
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "${1}" in
      --key)
        CLOUD_KEY="${2:-}"
        [[ -n "${CLOUD_KEY}" ]] || fail "--key requires a value"
        shift 2
        ;;
      --provision)
        RUN_STACKER_DEPLOY=true
        shift
        ;;
      --force-new)
        FORCE_NEW=true
        RUN_STACKER_DEPLOY=true
        shift
        ;;
      --deployment)
        DEPLOYMENT_HASH="${2:-}"
        [[ -n "${DEPLOYMENT_HASH}" ]] || fail "--deployment requires a value"
        shift 2
        ;;
      --plan)
        PLAN_ONLY=true
        shift
        ;;
      --apply-plan)
        APPLY_PLAN="${2:-}"
        [[ -n "${APPLY_PLAN}" ]] || fail "--apply-plan requires a value"
        shift 2
        ;;
      --no-force-app)
        FORCE_APP=false
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        fail "Unknown option: ${1}"
        ;;
    esac
  done
}

main() {
  parse_args "$@"

  require_file "${COMPOSE_SOURCE}" "Production compose file"
  require_file "${ENV_SOURCE}" "Environment file"
  require_file "${INIT_SQL_SOURCE}" "ClickHouse init SQL"

  if [[ "${RUN_STACKER_DEPLOY}" == true ]]; then
    run_stacker_deploy
    patch_base_url
  fi

  run_agent_deploy_app
}

main "$@"
