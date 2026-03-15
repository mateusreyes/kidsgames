#!/bin/bash
#
# Bootstrap script for the Basic Math game.
# Checks for updates from the git remote before launching.
# If the remote is unreachable, silently falls back to the local version.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

#######################################
# Print error message to stderr.
#######################################
err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

#######################################
# Check for updates and pull if behind.
# Falls back silently if the remote is unreachable.
#######################################
check_for_updates() {
  # Skip if not a git repo
  if [[ ! -d ".git" ]]; then
    return
  fi

  # Try to reach the remote; timeout after 5 seconds
  if ! git fetch --quiet 2>/dev/null; then
    # Remote is offline or unreachable — just use what we have
    return
  fi

  LOCAL_HEAD="$(git rev-parse HEAD 2>/dev/null)" || return
  REMOTE_HEAD="$(git rev-parse '@{u}' 2>/dev/null)" || return

  if [[ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]]; then
    echo "Update available, pulling latest changes..."
    if git pull --ff-only --quiet 2>/dev/null; then
      echo "Updated successfully. Launching new version..."
    else
      err "Auto-update failed (merge conflict?). Running current version."
    fi
  fi
}

# Maximum runtime before forcing a restart for update check (24 hours).
MAX_RUNTIME=86400

while true; do
  check_for_updates

  # Launch the game with a max runtime. timeout returns 124 when expired.
  set +e
  timeout "$MAX_RUNTIME" "$SCRIPT_DIR/start.sh"
  EXIT_CODE=$?
  set -e

  if [[ $EXIT_CODE -ne 124 ]]; then
    # User quit or error — exit normally, don't loop.
    exit $EXIT_CODE
  fi

  echo "Restarting for update check..."
done
