#!/bin/bash
# This script should be run from the project root directory (either directly or via `make create-migrations`)
set -e

# Start the Colima VM if running on local machine (for Docker runtime)
if [ "$(uname)" == "Darwin" ]; then
    colima start
fi
# Create migration files for the schema changes
atlas migrate diff --env project_config

# Set MigrationHash parameter of the MigrationTrigger custom resource in the CF template
./scripts/update_cfn_hash.sh
