#!/usr/bin/env bash
set -e

TAG=$1
if [ -z "$TAG" ]; then
  echo "usage: ./reset-demo.sh <tag>    e.g. ./reset-demo.sh demo/m3-base" >&2
  echo "available tags:" >&2
  git tag -l 'demo/*' | sed 's/^/  /' >&2
  exit 1
fi

if ! git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "no such tag: $TAG" >&2
  exit 1
fi

# Detach first, so resetting never drags a branch along with it. main must
# keep pointing at main, or the M7 pull request stops being a pull request.
git checkout -q --detach "$TAG"
git reset --hard -q "$TAG"
git clean -fdxq --exclude=.venv --exclude=node_modules
rm -rf .cursor/index .claude/cache 2>/dev/null || true

echo "Reset to $TAG (detached HEAD)."
echo
echo "RE-INDEX BEFORE RECORDING. The index cache has been deleted on purpose;"
echo "if you skip the re-index the tool answers from a stale index and the take"
echo "looks completely normal while being invalid."
