#!/usr/bin/env bash
set -e && [[ "$DEBUG" == 'true' ]] && set -x

# Install Atlas (required to create & validate DB schema migration files)
if ! command -v atlas &> /dev/null; then
  curl -sSf https://atlasgo.sh | sh
fi

function set_docker_socket_link() {
  # Set the docker socket link to the provided path, if it is not already set
  if [ "$(realpath /var/run/docker.sock)" != "$1" ]; then
    echo "Please enter your password to update the docker socket link"
    sudo ln -sf "$1" "/var/run/docker.sock"
  fi
}

# Install docker runtime (colima) on local Mac machine
# Docker engine should already be available in privileged CodeBuild environments
if [ "$(uname)" == "Darwin" ]; then
  if [ -d "/Applications/Docker.app" ]; then
    # Docker desktop is installed, make sure the docker socket is linked to the right location
    set_docker_socket_link "$HOME/.docker/run/docker.sock"
  else
    # Install docker cli if not available
    if ! command -v docker &> /dev/null; then
      brew install docker
      brew link docker
    fi
    # Install colima if not available
    if ! command -v colima &> /dev/null; then
      brew install colima
    fi

    # Set colima to start at login (and immediately)
    if ! brew services list | grep -q colima ; then
      brew services start colima  # Involves downloading a VM disk image the first time
    fi

    # Set colima as the default docker socket (See https://github.com/abiosoft/colima/issues/468#issuecomment-1306592238)
    set_docker_socket_link "$HOME/.colima/default/docker.sock"
    # fix credstore config if migrating from docker desktop (See https://stackoverflow.com/a/68202428)
    sed -i '' 's/desktop/colima/' ~/.docker/config.json
  fi
  # Download postgres 16-alpine image for local development
  docker pull postgres:16-alpine
fi
