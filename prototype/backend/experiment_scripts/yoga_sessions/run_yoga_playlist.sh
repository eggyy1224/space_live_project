#!/usr/bin/env bash

# Run Space Yoga playlist sequentially (scenes 1 → 5) with exclusive playback.
# - Stops any running script before starting the next
# - Polls /api/scripts/status until the current script finishes
# - Prints concise status updates with timestamps
#
# Usage:
#   bash scripts/run_yoga_playlist.sh
#   BASE_URL=http://localhost:8000 bash scripts/run_yoga_playlist.sh

set -euo pipefail

BASE_URL=${BASE_URL:-"http://localhost:8000"}
API_LIST="$BASE_URL/api/scripts/list"
API_EXEC="$BASE_URL/api/scripts/execute"
API_STATUS="$BASE_URL/api/scripts/status"
API_STOP_ALL="$BASE_URL/api/scripts/stop-all"

log() { printf "[%s] %s\n" "$(date '+%H:%M:%S')" "$*"; }

ensure_available() {
  local url=$1
  local name=$2
  for i in {1..20}; do
    if curl -fsS "$url" >/dev/null 2>&1; then return 0; fi
    sleep 0.5
  done
  log "ERROR: $name not reachable: $url"
  return 1
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

  # Validate scripts exist
  local want=(
    "yoga_sessions/space_yoga_teacher_baseline.sh"
    "yoga_sessions/space_yoga_teacher_baseline_scene2.sh"
    "yoga_sessions/space_yoga_teacher_baseline_scene3.sh"
    "yoga_sessions/space_yoga_teacher_baseline_scene4.sh"
    "yoga_sessions/space_yoga_teacher_baseline_scene5.sh"
  )

  local list_json
  list_json=$(curl -fsS "$API_LIST" || echo '{}')
  for s in "${want[@]}"; do
    if [[ "$list_json" != *"$s"* ]]; then
      log "ERROR: script not registered: $s"
      exit 1
    fi
  done

  log "Starting playlist (1 → 5)"
  for s in "${want[@]}"; do
    run_one "$s"
  done
  log "All scenes completed."
}

main "$@"

