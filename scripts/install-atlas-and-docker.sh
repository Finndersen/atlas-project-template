#!/usr/bin/env bash
set -e && [[ "$DEBUG" == 'true' ]] && set -x

# Install Atlas (required to create & validate DB schema migration files)
if ! command -v atlas &> /dev/null; then
  curl -sSf https://atlasgo.sh | sh
fi

if ! command -v colima &> /dev/null; then
  #  Install docker runtime on local Mac machine
  if [ "$(uname)" == "Darwin" ]; then
      read -r -p "If you are going to make changes to the DB schema, you need to install the Docker runtime. Enter 'y' to continue, or 'n' to skip: " yn
      if [ "$yn" == "y" ]; then
        brew install docker colima
        colima start  # Involves downloading a VM disk image the first time
      fi
  fi
fi

# Docker engine should already be available in privileged CodeBuild environments
