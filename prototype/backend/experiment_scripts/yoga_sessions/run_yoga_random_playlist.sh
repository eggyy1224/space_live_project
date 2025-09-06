#!/usr/bin/env bash

# Randomly pick N yoga scripts from yoga_sessions/ and play them sequentially.
# - Ensures exclusive playback (stop-all before each start)
# - Polls /api/scripts/status until current script finishes
# - Avoids selecting itself/helper scripts
#
# Usage examples:
#   bash prototype/backend/experiment_scripts/yoga_sessions/run_yoga_random_playlist.sh
#   bash prototype/backend/experiment_scripts/yoga_sessions/run_yoga_random_playlist.sh --count 3
#   BASE_URL=http://localhost:8000 bash prototype/backend/experiment_scripts/yoga_sessions/run_yoga_random_playlist.sh --count 5

set -euo pipefail

BASE_URL=${BASE_URL:-"http://localhost:8000"}
API_LIST="$BASE_URL/api/scripts/list"
API_EXEC="$BASE_URL/api/scripts/execute"
API_STATUS="$BASE_URL/api/scripts/status"
API_STOP_ALL="$BASE_URL/api/scripts/stop-all"

COUNT=3

while [[ $# -gt 0 ]]; do
  case "$1" in
    --count)
      COUNT=${2:-3}
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

log() { printf "[%s] %s\n" "$(date '+%H:%M:%S')" "$*"; }

ensure_available() {
  local url=$1 name=$2
  for i in {1..20}; do
    if curl -fsS "$url" >/dev/null 2>&1; then return 0; fi
    sleep 0.5
  done
  log "ERROR: $name not reachable: $url"
  return 1
}

# Extract script names from /api/scripts/list without requiring jq
extract_names() {
  # Pull all occurrences of "name":"..." safely without jq (BSD/macOS compatible)
  grep -oE '"name"\s*:\s*"[^"]+"' | sed -E 's/.*"name"\s*:\s*"([^"]+)"/\1/'
}

shuffle_array() {
  # Fisher–Yates shuffle on bash array
  # usage: shuffle_array arr[@] -> echoes space-separated shuffled items
  local arr=("${!1}")
  local i tmp j
  for ((i=${#arr[@]}-1; i>0; i--)); do
    j=$((RANDOM % (i+1)))
    tmp=${arr[i]}; arr[i]=${arr[j]}; arr[j]=$tmp
  done
  printf '%s\n' "${arr[@]}"
}

run_one() {
  local script_name=$1
  log "--- Stopping any running scripts (exclusive mode)"
  curl -fsS -X POST "$API_STOP_ALL" >/dev/null || true

  log ">>> Starting: $script_name"
  curl -fsS -X POST "$API_EXEC" -H "Content-Type: application/json" \
    -d "{\"script_name\":\"$script_name\",\"background\":true}" >/dev/null

  # Poll until the script disappears from running list
  local wait_s=0
  while true; do
    local st
    st=$(curl -fsS "$API_STATUS" || echo '{}')
    if [[ "$st" != *"$script_name"* ]]; then
      log "✔ Completed: $script_name (waited ${wait_s}s)"
      break
    fi
    if (( wait_s % 15 == 0 )); then
      log "... Running: $script_name (elapsed ${wait_s}s)"
    fi
    sleep 1
    wait_s=$((wait_s+1))
  done
}

main() {
  log "Checking backend endpoints..."
  ensure_available "$API_LIST" "list" || exit 1
  ensure_available "$API_STATUS" "status" || exit 1

  log "Fetching script pool from /api/scripts/list"
  local list_json
  list_json=$(curl -fsS "$API_LIST" || echo '{}')

  # Build pool from names under yoga_sessions/*.sh, excluding helpers/this runner
  # Accept: any .sh within yoga_sessions directory exposed by API
  local pool=()
  while IFS= read -r name; do
    # filters
    [[ "$name" != yoga_sessions/* ]] && continue
    [[ "$name" != *.sh ]] && continue
    [[ "$name" == *"_status_helpers.sh"* ]] && continue
    [[ "$name" == *"run_yoga_playlist.sh"* ]] && continue
    [[ "$name" == *"run_yoga_random_playlist.sh"* ]] && continue
    pool+=("$name")
  done < <(printf '%s' "$list_json" | extract_names)

  if (( ${#pool[@]} == 0 )); then
    log "ERROR: No eligible scripts found under yoga_sessions/."
    exit 1
  fi

  # Shuffle pool and pick first COUNT unique entries
  IFS=$'\n' read -r -d '' -a shuffled < <(shuffle_array pool[@] && printf '\0')

  local picks=()
  local n=0
  for s in "${shuffled[@]}"; do
    picks+=("$s")
    n=$((n+1))
    (( n >= COUNT )) && break
  done

  log "Playlist (random ${#picks[@]}/${COUNT}):"
  for p in "${picks[@]}"; do log " - $p"; done

  for s in "${picks[@]}"; do
    run_one "$s"
  done
  log "Random playlist completed."
}

main "$@"

