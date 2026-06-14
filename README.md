# whimsyhollow

Terraform infrastructure for an IAP-protected, scale-to-zero Cloud Run webapp,
deployed to a **single GCP project (`whimsyhollow`)** with `dev` / `test` / `prod`
partitioned *within* that one project.

## Single-project model

Unlike the multi-project scaffold this is derived from, every environment shares
the one `whimsyhollow` project. Isolation between `dev`/`test`/`prod` comes from
two axes instead of separate projects:

- **State** — one tfstate bucket (`whimsyhollow-tfstate`), partitioned by GCS
  prefix: `terraform/state/<env>/<stack>`.
- **Resources** — every env-scoped resource is namespaced with `-<env>` (or
  `_<env>` for BigQuery), e.g. Cloud Run `agentic-webapp-<env>`.

## Layout

```
infra/                  Terraform (stacks + modules), the tfs lifecycle CLI, bootstrap scripts
.github/workflows/      Per-stack Terraform CI/CD (reusable workflow + composite action)
```

Start at [`infra/README.md`](infra/README.md). Quickstart:

```bash
make -C infra help          # list every target
make -C infra ci            # no-cloud gate: fmt-check + lint + validate + tfs tests
make -C infra plan-dev      # terraform plan for STACK=webapp against the dev partition
```
