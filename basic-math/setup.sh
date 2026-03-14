#!/bin/bash
#
# Sets up the Python virtual environment and installs required system
# dependencies for the Basic Math game on Ubuntu.

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

  echo "Installing Ubuntu system requirements..."
  sudo apt-get update
  sudo apt-get install -y python3-venv python3-dev python3-pip git

  echo "Creating Python virtual environment..."
  python3 -m venv .venv

  echo "Activating virtual environment..."
  source .venv/bin/activate || {
    err "Failed to activate virtual environment."
    exit 1
  }

  echo "Installing dependencies..."
  # Upgrade pip just in case
  pip install --upgrade pip

  # Install required packages
  pip install pygame

  echo "Setup complete! You can now run './start.sh' to play."
}

main "$@"