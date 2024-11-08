#!/bin/bash
# This script is used to download the Atlas binary to be included in the Lambda Layer
# Should be run from the project root directory, like ./scripts/download_atlas_binary.sh
DESTINATION_DIR=$1
mkdir -p "$DESTINATION_DIR"
curl -o "$DESTINATION_DIR/atlas" https://release.ariga.io/atlas/atlas-linux-amd64-v0.28.2-0c6632d-canary
chmod +x "$DESTINATION_DIR/atlas"

expected_checksum="44156686ed235d34491b06117d63a2ae83981302b84f4f160537a85ec7928dd8"
actual_checksum=$(sha256sum "$DESTINATION_DIR/atlas" | awk '{print $1}')

if [ "$actual_checksum" != "$expected_checksum" ]; then
  echo "Checksum mismatch for downloaded Atlas binary"
  exit 1
fi
