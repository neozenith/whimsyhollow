# Root Makefile — the single command-and-control surface (see the global working-dir
# rule). `make fix` / `make ci` fan out to every subproject's own fix/ci target.
SHELL         := /usr/bin/env bash
.SHELLFLAGS   := -eu -o pipefail -c
.DEFAULT_GOAL := help

# Order: backend first (the SPA + API), then frontend, then infra. e2e is driven
# separately (it boots both servers) via `make e2e`.
SUBPROJECTS := backend frontend infra

# Local dev ports — FastAPI backend, Vite SPA.
DEV_PORTS := 8080 5173

# NOTE: ci-%/fix-% are deliberately NOT in .PHONY — GNU Make 3.81 (macOS default)
# suppresses a pattern rule whose instances are listed as .PHONY ("Nothing to be
# done"). They fire correctly without it since no real files of those names exist.
.PHONY: help install dev clean-ports fix ci e2e

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_/-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install/sync deps in every subproject
	@for d in $(SUBPROJECTS); do echo ">>> install $$d"; $(MAKE) -C $$d install; done

dev: ## Run the webapp locally: FastAPI :8080 + Vite :5173 (Ctrl-C stops both) — open http://localhost:5173
	bun run --cwd frontend dev

clean-ports: ## Kill any stray processes holding the local dev ports (8080 backend, 5173 frontend)
	@for p in $(DEV_PORTS); do \
	  pid=$$(lsof -ti:$$p 2>/dev/null || true); \
	  if [ -n "$$pid" ]; then kill -9 $$pid && echo "💣 killed PID $$pid on port $$p"; else echo "✅ port $$p free"; fi; \
	done

fix: ## Auto-fix (format + lint) across backend + frontend
	@for d in backend frontend; do echo ">>> fix $$d"; $(MAKE) -C $$d fix; done

ci: ## Run the full QA gate (lint + strict types + tests) across every subproject
	@for d in $(SUBPROJECTS); do echo ">>> ci $$d"; $(MAKE) -C $$d ci; done

e2e: ## Run the Playwright e2e suite (boots backend + frontend; needs `make -C e2e install` once)
	$(MAKE) -C e2e test

# Per-subproject escape hatches: `make ci-backend`, `make fix-frontend`, …
ci-%: ## Run ci for one subproject (e.g. make ci-backend)
	$(MAKE) -C $* ci

fix-%: ## Run fix for one subproject (e.g. make fix-frontend)
	$(MAKE) -C $* fix
