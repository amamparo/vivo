#!/usr/bin/env bash
# Determine the next release version.
#
# Usage: resolve-version.sh [requested-version]
#   If requested-version is provided (e.g. v1.2.3), validates it.
#   Otherwise, bumps the minor version from the latest git tag.
#
# Outputs (via GITHUB_OUTPUT if set, otherwise stdout):
#   new_version  — bare semver (e.g. 1.2.0)
#   new_tag      — prefixed tag (e.g. v1.2.0)
#   skip         — "true" if there's nothing to release
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
REQUESTED="${1:-}"

if [ -n "$REQUESTED" ]; then
  NEW_TAG="$REQUESTED"
  NEW_BARE="${NEW_TAG#v}"

  if ! echo "$NEW_BARE" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "::error::Version must be in vX.Y.Z semver format, got: $NEW_TAG" >&2
    exit 1
  fi

  if git rev-parse "$NEW_TAG" >/dev/null 2>&1; then
    echo "::error::Tag $NEW_TAG already exists" >&2
    exit 1
  fi

  if [ "$(printf '%s\n' "$CURRENT_BARE" "$NEW_BARE" | sort -V | tail -1)" = "$CURRENT_BARE" ] && [ "$CURRENT_BARE" != "0.0.0" ]; then
    echo "::error::Version $NEW_TAG is not greater than current $CURRENT" >&2
    exit 1
  fi
else
  # Auto mode: skip if HEAD is already tagged
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
fi

echo "Releasing: $NEW_TAG (was $CURRENT)"
output skip false
output new_version "$NEW_BARE"
output new_tag "$NEW_TAG"
