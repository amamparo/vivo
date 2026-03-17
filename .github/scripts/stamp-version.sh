#!/usr/bin/env bash
# Stamp a version string into all project files (working copy only, not committed).
#
# Usage: stamp-version.sh <version>
#   e.g. stamp-version.sh 1.2.0
set -euo pipefail

VERSION="$1"

jq --arg v "$VERSION" '.version = $v' src-tauri/tauri.conf.json > tmp.json && mv tmp.json src-tauri/tauri.conf.json
sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" src-tauri/Cargo.toml
sed -i '' "s/^__version__ = .*/__version__ = \"$VERSION\"/" remote_script/__init__.py

echo "Stamped version $VERSION into project files"
