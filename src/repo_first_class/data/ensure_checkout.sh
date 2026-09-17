#!/usr/bin/env bash
# ensure_checkout.sh <owner/repo> <dest>
# Clone the repo to <dest> if missing; ff-only pull if present.
# Prints: VISIBILITY, LOCAL_HEAD, REMOTE_HEAD. Exits non-zero on divergence.
set -euo pipefail

REPO="${1:?usage: ensure_checkout.sh <owner/repo> <dest>}"
DEST="${2:?usage: ensure_checkout.sh <owner/repo> <dest>}"
BRANCH="$(gh repo view "$REPO" --json defaultBranchRef --jq .defaultBranchRef.name)"
VIS="$(gh repo view "$REPO" --json visibility --jq .visibility)"

if [ -d "$DEST/.git" ]; then
  git -C "$DEST" pull --ff-only --quiet
else
  mkdir -p "$(dirname "$DEST")"
  gh repo clone "$REPO" "$DEST" -- --quiet
fi

LOCAL_HEAD="$(git -C "$DEST" rev-parse HEAD)"
REMOTE_HEAD="$(gh api "repos/$REPO/commits/$BRANCH" --jq .sha)"
DIRTY="$(git -C "$DEST" status --short | head -5)"

echo "VISIBILITY=$VIS"
echo "BRANCH=$BRANCH"
echo "LOCAL_HEAD=$LOCAL_HEAD"
echo "REMOTE_HEAD=$REMOTE_HEAD"
[ -n "$DIRTY" ] && { echo "DIRTY:"; echo "$DIRTY"; }
if [ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]; then
  echo "DIVERGED: local HEAD != remote HEAD (needs merge, not ff-only)" >&2
  exit 2
fi
echo "IN_SYNC=1"
