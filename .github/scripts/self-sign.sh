#!/usr/bin/env bash
# Create a temporary self-signed certificate and sign the Tauri app bundle.
# This gives the app a valid code signature so macOS shows "Open Anyway"
# in System Settings instead of the "damaged" error.
#
# Usage: self-sign.sh <path-to-app-bundle>
#   e.g. self-sign.sh src-tauri/target/aarch64-apple-darwin/release/bundle/macos/Vivo.app
set -euo pipefail

APP_PATH="$1"

if [ ! -d "$APP_PATH" ]; then
  echo "App bundle not found: $APP_PATH"
  exit 1
fi

KEYCHAIN="build.keychain"
KEYCHAIN_PASS="ci-build"
CERT_NAME="Vivo Self-Signed"

# Create a self-signed certificate
cat > /tmp/cert.conf <<EOF
[req]
distinguished_name = req_dn
x509_extensions = v3_code
prompt = no

[req_dn]
CN = $CERT_NAME

[v3_code]
keyUsage = digitalSignature
extendedKeyUsage = codeSigning
EOF

openssl req -x509 -newkey rsa:2048 -keyout /tmp/cert.key -out /tmp/cert.pem \
  -days 1 -nodes -config /tmp/cert.conf 2>/dev/null
openssl pkcs12 -export -out /tmp/cert.p12 -inkey /tmp/cert.key -in /tmp/cert.pem \
  -passout pass:"$KEYCHAIN_PASS"

# Import into a temporary keychain
security create-keychain -p "$KEYCHAIN_PASS" "$KEYCHAIN"
security set-keychain-settings "$KEYCHAIN"
security unlock-keychain -p "$KEYCHAIN_PASS" "$KEYCHAIN"
security import /tmp/cert.p12 -k "$KEYCHAIN" -P "$KEYCHAIN_PASS" -T /usr/bin/codesign
security set-key-partition-list -S apple-tool:,apple: -s -k "$KEYCHAIN_PASS" "$KEYCHAIN"
security list-keychains -d user -s "$KEYCHAIN" $(security list-keychains -d user | tr -d '"')

# Sign the app bundle
codesign --force --deep --sign "$CERT_NAME" "$APP_PATH"
echo "Signed: $APP_PATH"

# Verify
codesign --verify --verbose "$APP_PATH"

# Cleanup
security delete-keychain "$KEYCHAIN"
rm -f /tmp/cert.conf /tmp/cert.key /tmp/cert.pem /tmp/cert.p12
