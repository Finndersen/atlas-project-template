#!/bin/bash
# Set MigrationHash parameter of the MigrationTrigger custom resource in the CF template,
# to the value of the hash of the migration files
# Should be run from the project root directory
atlas_checksum=$(head -n 1 src/db/migrations/atlas.sum | cut -c 4-)
# Use | separator for sed because checksum might contain /
sed -i '' "s|\(      MigrationHash: \).*|\1$atlas_checksum|" "cloud-formation.yaml"
