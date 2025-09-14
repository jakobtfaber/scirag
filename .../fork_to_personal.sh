#!/usr/bin/env bash

set -euo pipefail

# This script converts an existing local clone of a GitHub repo into your personal fork workflow.
# It will:
#  - Verify Git and GitHub CLI state
#  - Create a fork under your GitHub account (if it doesn't exist)
#  - Rewire remotes so that:
#       origin   -> your fork
#       upstream -> the original repo
#  - Optionally auto-commit any local changes
#  - Push all local branches and tags to your fork
#
# Usage:
#   scripts/fork_to_personal.sh [--owner <github_username>] [--https] [--auto-commit] [--commit-message "msg"]
#
# Defaults:
#   --owner          defaults to the active gh auth account
#   SSH vs HTTPS     defaults to SSH remotes unless --https is provided
#   auto-commit      disabled by default; if enabled without --commit-message, a default message is used

OWNER=""
USE_HTTPS=false
AUTO_COMMIT=false
COMMIT_MSG="chore: auto-commit local changes before forking"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner)
      OWNER="$2"; shift 2 ;;
    --https)
      USE_HTTPS=true; shift ;;
    --auto-commit)
      AUTO_COMMIT=true; shift ;;
    --commit-message)
      COMMIT_MSG="$2"; shift 2 ;;
    -h|--help)
      sed -n '1,60p' "$0"; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Ensure we are inside a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a git repository." >&2
  exit 1
fi

# Check GitHub CLI availability
if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI 'gh' not found. Install from https://cli.github.com/" >&2
  exit 1
fi

# Verify auth and determine default owner if not provided
if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "Error: Not authenticated to GitHub. Run: gh auth login" >&2
  exit 1
fi

if [[ -z "$OWNER" ]]; then
  OWNER=$(gh api user --jq .login)
fi

# Discover current origin (original upstream) repo info
if ! git config remote.origin.url >/dev/null; then
  echo "Error: remote 'origin' not found. Please add the original repo as 'origin' and retry." >&2
  exit 1
fi

ORIGIN_URL=$(git config remote.origin.url)

# Normalize to https URL to parse owner/name reliably
URL_CANON="$ORIGIN_URL"
if [[ "$URL_CANON" == git@github.com:* ]]; then
  URL_CANON="https://github.com/${URL_CANON#git@github.com:}"
fi
URL_CANON=${URL_CANON%.git}

REPO_PATH=${URL_CANON#https://github.com/}
UPSTREAM_OWNER=${REPO_PATH%%/*}
REPO_NAME=${REPO_PATH##*/}

if [[ -z "$UPSTREAM_OWNER" || -z "$REPO_NAME" ]]; then
  echo "Error: failed to parse origin URL '$ORIGIN_URL'" >&2
  exit 1
fi

echo "Detected original repo: $UPSTREAM_OWNER/$REPO_NAME"
echo "Target fork owner:      $OWNER"

# Optionally auto-commit any local changes (staged or unstaged)
if $AUTO_COMMIT; then
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Auto-committing local changes..."
    git add -A
    git commit -m "$COMMIT_MSG" || true
  fi
fi

# Create the fork if it does not exist
echo "Ensuring fork exists at $OWNER/$REPO_NAME ..."
if ! gh repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1; then
  gh repo fork "$UPSTREAM_OWNER/$REPO_NAME" --remote=false >/dev/null
  echo "Fork created: https://github.com/$OWNER/$REPO_NAME"
else
  echo "Fork already exists."
fi

# Determine fork URL (SSH or HTTPS)
if $USE_HTTPS; then
  FORK_URL="https://github.com/$OWNER/$REPO_NAME.git"
else
  # Prefer SSH if available
  FORK_URL=$(gh repo view "$OWNER/$REPO_NAME" --json sshUrl --jq .sshUrl)
fi

# Rewire remotes: origin -> fork, upstream -> original
if git remote get-url upstream >/dev/null 2>&1; then
  # upstream exists; ensure it points to original
  git remote set-url upstream "$ORIGIN_URL"
else
  git remote rename origin upstream
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$FORK_URL"
else
  git remote add origin "$FORK_URL"
fi

echo "Remotes configured:"
git remote -v

echo "Fetching all remotes..."
git fetch --all --prune

echo "Pushing all branches to origin (fork)..."
git push --all origin

echo "Pushing all tags to origin (fork)..."
git push --tags origin || true

echo "Done. Your local repo now tracks:"
echo "  origin   -> $OWNER/$REPO_NAME"
echo "  upstream -> $UPSTREAM_OWNER/$REPO_NAME"

echo "Tips:"
echo "  - To sync from upstream: git fetch upstream && git checkout main && git merge upstream/main && git push origin main"
echo "  - To auto-commit next time: add --auto-commit [--commit-message 'msg']"


