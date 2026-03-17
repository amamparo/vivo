#!/usr/bin/env bash
# Determine the next release version by bumping the minor version.
# If HEAD is already tagged, reuse that tag (supports retries).
#
# Outputs (via GITHUB_OUTPUT if set, otherwise stdout):
#   new_version    — bare semver (e.g. 1.2.0)
#   new_tag        — prefixed tag (e.g. v1.2.0)
#   prev_tag       — previous tag for changelog links
#   already_tagged — "true" if HEAD already has a tag
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

# If HEAD is already tagged, reuse it (retry-safe)
if [ "$CURRENT" != "v0.0.0" ] && [ "$(git rev-list -1 "$CURRENT" 2>/dev/null)" = "$(git rev-parse HEAD)" ]; then
  PREV=$(git describe --tags --abbrev=0 "$CURRENT^" 2>/dev/null || echo "v0.0.0")
  echo "HEAD is already tagged $CURRENT — reusing for build"
  output new_version "$CURRENT_BARE"
  output new_tag "$CURRENT"
  output prev_tag "$PREV"
  output already_tagged true
  exit 0
fi

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_BARE"
MINOR=$((MINOR + 1))
NEW_BARE="${MAJOR}.${MINOR}.0"
NEW_TAG="v${NEW_BARE}"

echo "Releasing: $NEW_TAG (was $CURRENT)"
output new_version "$NEW_BARE"
output new_tag "$NEW_TAG"
output prev_tag "$CURRENT"
output already_tagged false
