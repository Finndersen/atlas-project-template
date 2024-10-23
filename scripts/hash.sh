#!/bin/bash
# Updates the Atlas checksum file and the MigrationHash parameter in the CF template
# This script should be run from the project root directory (either directly or via `make hash-migrations`)
set -e

# Re-generate Atlas migration hash file
atlas migrate hash --env project_config

# Set MigrationHash parameter of the MigrationTrigger custom resource in the CF template
./scripts/update_cfn_hash.sh
