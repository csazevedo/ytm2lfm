# Makefile for ytm2lfm Project

# Configuration
PROJECT_NAME = ytm2lfm
CLI_PATH := ./src/cli.py

.DEFAULT_GOAL := help

.PHONY: help
help:  ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Environment Setup

.PHONY: sync
sync:  ## Sync dependencies
	@uv sync

##@ Development Tasks

.PHONY: test
test:  ## Run tests
	@uv run pytest -v

.PHONY: typing
typing:
	@uv run mypy src

.PHONY: lint
lint:  ## Runs linter
	@uv run ruff check --select I,E .

.PHONY: lint-and-fix
lint-and-fix:  ## Runs linter and fixes automatically
	@uv run ruff check --select I,E --fix --unsafe-fixes .
	@uv run ruff format .

##@ Cleanup

.PHONY: clean
clean:  ## Remove virtual environment and artifacts to reset the project to a clean state.
	@echo "Cleaning project..."
	rm -rf __pycache__
	rm -rf ytm2lfm/__pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	@echo "Clean complete"

##@ Running Application

.PHONY: scrobble
scrobble:  ## Run the scrobbler to send tracks to Last.fm
	uv run $(CLI_PATH) scrobble

.PHONY: store
store:  ## Store tracks without scrobbling
	uv run $(CLI_PATH) store

.PHONY: dry-run
dry-run:  ## Run without side effects (scrobbling or storing)
	uv run $(CLI_PATH) dry-run

##@ Running Application with Docker

.PHONY: docker-scrobble
docker-scrobble:  ## Run the scrobbler in Docker to send tracks to Last.fm
	docker compose run --rm app python $(CLI_PATH) scrobble

.PHONY: docker-store
docker-store:  ## Store tracks without scrobbling using Docker
	docker compose run --rm app python $(CLI_PATH) store

.PHONY: docker-dry-run
docker-dry-run:  ## Run in Docker without side effects (scrobbling or storing)
	docker compose run --rm app python $(CLI_PATH) dry-run

.PHONY: docker-shell
docker-shell:  ## Run an interactive shell in the container for debugging
	docker compose run --rm app sh
