#!/bin/bash
# This script is used to download the Atlas binary to be included in the Lambda Layer
# Should be run from the project root directory, like ./scripts/download_atlas_binary.sh
DESTINATION_DIR=$1
mkdir -p "$DESTINATION_DIR"
curl -o "$DESTINATION_DIR/atlas" https://release.ariga.io/atlas/atlas-linux-amd64-v0.28.0
chmod +x "$DESTINATION_DIR/atlas"

expected_checksum="f43bd5eccedb2b719178aa132cdac0f3459039134368cf9e3aa3d0a4ca852f9b"
actual_checksum=$(sha256sum "$DESTINATION_DIR/atlas" | awk '{print $1}')

if [ "$actual_checksum" != "$expected_checksum" ]; then
  echo "Checksum mismatch for downloaded Atlas binary"
  exit 1
fi
