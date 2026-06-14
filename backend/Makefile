# backend/Makefile — the whimsyhollow FastAPI service.
# Run from backend/, or `make -C backend <target>` from the repo root.

SHELL       := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

IMAGE ?= whimsyhollow-backend:local
PORT  ?= 8080

.PHONY: help install dev start format lint typecheck test ci docker-build docker-run

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Sync the venv from uv.lock
	uv sync

dev: ## Run locally with hot reload at http://localhost:$(PORT)
	uv run uvicorn whimsyhollow.main:app --reload --host 0.0.0.0 --port $(PORT)

start: ## Run locally without reload (production entrypoint)
	uv run uvicorn whimsyhollow.main:app --host 0.0.0.0 --port $(PORT)

format: ## Auto-format + fix
	uvx ruff format . --line-length 120
	uvx ruff check . --line-length 120 --fix-only

lint: ## Lint — any finding fails
	uvx ruff check src tests --line-length 120

typecheck: ## Strict type-check (mypy --strict via pyproject)
	uv run mypy src

test: ## Run the test suite (real impls, no mocks)
	uv run pytest -q

ci: lint typecheck test ## Full QA gate (lint + strict types + tests >=90% coverage)

docker-build: ## Build the container image (repo-root context so frontend is included)
	docker build -f Dockerfile -t $(IMAGE) ..

docker-run: ## Run the container locally at http://localhost:$(PORT)
	docker run --rm -p $(PORT):8080 -e PORT=8080 $(IMAGE)
