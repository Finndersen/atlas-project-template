SHELL := /bin/bash

# Atlas and Docker runtime are required for creating and validating DB migration files
.PHONY: install
install:
	@pip install -e .[dev]
	@scripts/install-atlas-and-docker.sh

.PHONY: lint
lint:
	@ruff check
	@ruff format --check
	@python -m pyright
	@make check-migrations

.PHONY: format
format:
	@ruff format
	@ruff check --fix

.PHONY: test
test:
	@pytest

.PHONY: create-migrations
create-migrations:
	@scripts/create.sh

.PHONY: check-migrations
check-migrations:
	@scripts/check.sh

.PHONY: hash-migrations
hash-migrations:
	@scripts/hash.sh
