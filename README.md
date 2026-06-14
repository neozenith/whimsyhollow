# whimsyhollow

A scale-to-zero Cloud Run web app — a plain **FastAPI** backend serving a **React + Vite**
SPA — deployed to a **single GCP project (`whimsyhollow`)** with `dev` / `test` / `prod`
partitioned *within* that one project.

## Layout

```
backend/    FastAPI (uv) — JSON API (/api/health, /api/me) + serves the built SPA
frontend/   React + Vite + TypeScript + Tailwind v4 + shadcn/ui (bun)
e2e/        Playwright smoke suite (boots backend + frontend)
infra/      Terraform (stacks + modules), the tfs lifecycle CLI, bootstrap scripts
.github/    CI: app-ci.yml (backend/frontend/e2e) + terraform-cicd-*.yml
```

## App features

The frontend is a minimal app shell carrying:

- **Dark/light theme provider** — toggled from the header; persisted + respects OS preference.
- **Live brand switcher** ("rapid theme changer") — swaps brand token packs at runtime from the header.
- **Collapsible sidebar** for navigating pages (with an off-canvas mobile drawer).
- **Global header bar** showing the logged-in user (from `/api/me`) + the deployment environment.
- **Playwright e2e** smoke suite covering all of the above.

## Quickstart

```bash
make install        # sync backend (uv) + frontend (bun) deps
make dev            # FastAPI :8080 + Vite :5173 — open http://localhost:5173
make ci             # lint + strict types + unit tests across backend + frontend + infra
make e2e            # Playwright smoke suite (run `make -C e2e install` once for browsers)
make fix            # auto-format + lint-fix backend + frontend
```

## Single-project infra model

Every environment shares the one `whimsyhollow` project; isolation between `dev`/`test`/`prod`
comes from two axes instead of separate projects:

- **State** — one tfstate bucket (`whimsyhollow-tfstate`), partitioned by GCS prefix
  `terraform/state/<env>/<stack>`.
- **Resources** — every env-scoped resource is namespaced with `-<env>` (or `_<env>` for
  BigQuery), e.g. Cloud Run `whimsyhollow-<env>`.

See [`infra/README.md`](infra/README.md) for the full infra story.
