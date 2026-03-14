#!/bin/bash
#
# Starts the Basic Math game by activating the virtual environment
# and running the main Python script.

set -euo pipefail

#######################################
# Print error message to stderr.
# Globals:
#   None
# Arguments:
#   Message to print
#######################################
err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

#######################################
# Main execution function.
# Globals:
#   None
# Arguments:
#   None
#######################################
main() {
  cd "$(dirname "$0")" || {
    err "Failed to change directory."
    exit 1
  }

  if [[ ! -f ".venv/bin/activate" ]]; then
    err "Virtual environment not found. Please run ./setup.sh first."
    exit 1
  fi

  # Shellcheck might complain about source, but it's fine for bash.
  source .venv/bin/activate || {
    err "Failed to activate virtual environment."
    exit 1
  }

  python3 math.py
}

main "$@"
