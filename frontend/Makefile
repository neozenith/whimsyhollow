# frontend/Makefile — thin wrapper over the bun scripts in package.json so the
# root Makefile can delegate uniformly (`make -C frontend ci`). Always bun.
SHELL       := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.PHONY: install dev fix lint typecheck test build ci

install: ## Install deps (bun)
	bun install

dev: ## Run backend + Vite together (http://localhost:5173)
	bun run dev

fix: ## Auto-fix formatting + lint (biome --write)
	bun run fix

lint: ## Lint (biome, warnings = errors)
	bun run lint

typecheck: ## Type-check (tsc --noEmit)
	bun run typecheck

test: ## Unit tests + coverage (vitest)
	bun run test

build: ## Production build (tsc + vite build → dist/)
	bun run build

ci: lint typecheck test ## Full frontend QA gate
