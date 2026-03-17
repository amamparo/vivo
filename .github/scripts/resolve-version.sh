#!/usr/bin/env bash
# Determine the next release version by bumping the minor version.
#
# Outputs (via GITHUB_OUTPUT if set, otherwise stdout):
#   new_version  — bare semver (e.g. 1.2.0)
#   new_tag      — prefixed tag (e.g. v1.2.0)
#   skip         — "true" if HEAD is already tagged
set -euo pipefail

output() {
  if [ -n "${GITHUB_OUTPUT:-}" ]; then
    echo "$1=$2" >> "$GITHUB_OUTPUT"
  else
    echo "$1=$2"
  fi
}

CURRENT=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
CURRENT_BARE="${CURRENT#v}"

# Skip if HEAD is already tagged
if [ "$CURRENT" != "v0.0.0" ] && [ "$(git rev-list -1 "$CURRENT" 2>/dev/null)" = "$(git rev-parse HEAD)" ]; then
  echo "HEAD is already tagged $CURRENT — nothing to release"
  output skip true
  exit 0
fi

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_BARE"
MINOR=$((MINOR + 1))
NEW_BARE="${MAJOR}.${MINOR}.0"
NEW_TAG="v${NEW_BARE}"

# Safety: if this tag somehow already exists, skip
if git rev-parse "$NEW_TAG" >/dev/null 2>&1; then
  echo "Tag $NEW_TAG already exists — nothing to release"
  output skip true
  exit 0
fi

echo "Releasing: $NEW_TAG (was $CURRENT)"
output skip false
output new_version "$NEW_BARE"
output new_tag "$NEW_TAG"
