# e2e/Makefile — Playwright smoke suite for the whimsyhollow app shell.
# Run from the repo root, e.g.  make -C e2e test
SHELL       := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# By default the suite boots the local backend + frontend itself (see playwright.config.ts
# webServer). Override BASE_URL to point at a deployed env: make -C e2e test BASE_URL=https://...
BASE_URL ?=

.PHONY: help install test mobile list report

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install deps + the chromium & webkit browsers (webkit drives the iPhone 11 project)
	bun install
	bun run install-browser

test: ## Run the full suite; boots backend+frontend locally unless BASE_URL is set
	BASE_URL=$(BASE_URL) bun run test

mobile: ## Run ONLY the iPhone 11 mobile-layout suite
	BASE_URL=$(BASE_URL) bun run test --project=iphone-11

list: ## List discovered tests without running them (validates the suite structure)
	bunx playwright test --list

report: ## Open the last HTML report
	bun run report
