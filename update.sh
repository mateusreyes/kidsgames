#!/bin/bash
#
# Pulls the latest version from git and reinstalls dependencies
# if requirements changed.

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

  echo "Pulling latest changes..."
  local remote branch
  remote=$(git remote | head -n1)
  branch=$(git branch --show-current)

  # Only pull if the remote branch exists.
  if git ls-remote --exit-code --heads "${remote}" "${branch}" > /dev/null 2>&1; then
    # Set upstream tracking if not configured yet.
    if ! git config "branch.${branch}.remote" > /dev/null 2>&1; then
      echo "Setting upstream to ${remote}/${branch}..."
      git branch --set-upstream-to="${remote}/${branch}" "${branch}"
    fi

    git pull --ff-only || {
      err "Git pull failed. You may have local changes — resolve them manually."
      exit 1
    }
  else
    echo "Remote branch '${remote}/${branch}' not found — skipping pull."
    echo "Push first with: git push ${remote} ${branch}"
  fi

  if [[ ! -d "basic-math/.venv" ]]; then
    echo "Virtual environment not found. Running setup..."
    bash basic-math/setup.sh
    return
  fi

  echo "Updating dependencies..."
  source basic-math/.venv/bin/activate || {
    err "Failed to activate virtual environment."
    exit 1
  }

  pip install --upgrade pygame

  echo "Update complete! Run './start.sh' to play."
}

main "$@"
