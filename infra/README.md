# `infra/` — Terraform (stacks + modules)

Terraform for the **whimsyhollow**, organised as **independently-deployed
stacks** (each with its own GCS state) composed from **reusable modules**. The
same `*.tf` in a stack plan/apply against the **single `whimsyhollow` GCP
project**, where dev/test/prod are **partitions within that one project**
(not separate projects), selected via **partial backend configuration**.

> **Single-project namespacing:** this repo OWNS the `whimsyhollow` project.
> dev/test/prod are not separate projects — they share the one project, so
> every env-scoped resource is namespaced with `-<env>` (or `_<env>` for
> BigQuery, which disallows hyphens), and tfstate is partitioned by an
> env-in-prefix inside one bucket. See
> [Single-project namespacing](#single-project-namespacing).

## The model

1. **Bootstrap = bare minimum.** Once for the project: one GCS state bucket
   (`whimsyhollow-tfstate`) + the `whimsyhollow-deployer` SA + one OIDC provider
   in one WIF pool (`github-pool`) that this repo's CI impersonates. Run directly
   against GCP (`bootstrap/`), never through Terraform.
2. **A stack is one cohesive, independently-deployable definition.** `webapp` is
   *the IAP-protected Cloud Run service* — kept whole. Independence comes from
   adding **new** stacks, not from splitting an existing one.
3. **One workflow per stack** promotes it through dev → test → prod.
4. **Many stacks, one bucket total, state namespaced by env then stack** —
   `prefix = "terraform/state/<env>/<stack>"`, uniformly (no exceptions). The
   environment is part of the prefix, so all three envs live in the one bucket
   without colliding.
5. **Primitives become modules** once a second stack reuses them — extracted from
   real reuse, not anticipated.

## Layout

```
infra/
├── bootstrap/              one-time GCP + GitHub setup scripts (see bootstrap/README.md)
├── config.yml             per-env GCP settings consumed by the scaffolder
├── Makefile               STACK-aware wrapper around terraform + tooling (default STACK=webapp)
├── .tflint.hcl            tflint config (recursive across stacks + modules)
├── modules/               reusable building blocks (see modules/README.md)
│   └── <module>/
├── tfs/                    the `tfs` stack-lifecycle CLI (installable uv tool — see tfs/README.md)
│   └── src/tfs/           argparse app + commands/ + packaged scaffolding templates/
└── stacks/
    └── webapp/            the Cloud Run + IAP stack (scales to zero, single-user IAP)
        ├── backend.tf  provider.tf  main.tf  variables.tf  cloudrun.tf  iap.tf  outputs.tf
        ├── README.md
        └── backends/{dev,test,prod}.config
```

## Quickstart

```bash
make -C infra help                       # list every target
make -C infra plan-dev                   # plan STACK (default webapp) against dev
make -C infra apply-dev                  # apply
make -C infra STACK=webapp plan-prod
make -C infra ci                         # no-cloud gate: fmt-check + security + validate + gha-check
```

The `tfs` CLI is the streamlined path (it adds a `gcloud` project guardrail and
wires the terraform flags). Install it once as a uv tool and call it anywhere:

```bash
uv tool install 'tfs @ ./infra/tfs'      # from the repo root; then, anywhere in the repo:
tfs plan  webapp dev
tfs apply webapp dev
```

Or run it without installing (what the Makefile + CI do — no global state):

```bash
uv run --directory infra/tfs tfs plan  webapp dev
uv run --directory infra/tfs tfs apply webapp dev
```

## Single-project namespacing

All three environments share the one `whimsyhollow` project, so isolation is by
**name**, not by project. Every env-scoped resource carries a `-<env>` suffix
(`_<env>` for BigQuery). The `webapp` stack defines these as `locals` in
`stacks/webapp/main.tf` (with `project_id` pinned to the constant
`"whimsyhollow"`):

| Resource | Name | Local |
|---|---|---|
| Cloud Run service | `whimsyhollow-<env>` | `name` |
| Runtime SA | `whimsyhollow-run-<env>` | `runtime_sa_id` |
| Artifact Registry repo | `whimsyhollow-<env>` | `repository_id` |
| GCS assets bucket | `whimsyhollow-whimsyhollow-assets-<env>` | `assets_bucket` |
| BigQuery dataset | `whimsyhollow_<env>` | `bq_dataset_id` |
| Firestore named DB | `whimsyhollow-<env>` | `firestore_name` |

**Project-level resources are co-owned by all three env state files.** The
`google_project_service` API enables and the project-level IAM
(`*_iam_member`) bindings are referenced from each env's state. This is safe:
API enables are idempotent with `disable_on_destroy = false`, and the IAM
bindings are additive, each referencing that env's distinct runtime SA — so the
three envs never clobber one another within the shared project.

## Adding a new stack

```bash
make -C infra create-stack NAME=monitoring
# or: tfs create monitoring   (or: uv run --directory infra/tfs tfs create monitoring)
```

This scaffolds `stacks/monitoring/` (backend/provider/main/variables `.tf`,
per-env `backends/*.config`, a `README.md`) **and** the matching CI caller
`.github/workflows/terraform-cicd-stack-monitoring.yml`. Then:

```bash
make -C infra gha-check                              # confirm stack ↔ workflow coverage
make -C infra STACK=monitoring validate-all          # init + validate every env
```

## State management

- **One tfstate bucket total** — `whimsyhollow-tfstate`. Every stack and every
  environment shares this single bucket.
- **One state object per env per stack**, isolated by GCS `prefix` (env first,
  then stack):

  | Stack | `prefix` | Why |
  |---|---|---|
  | *every stack* | `terraform/state/<env>/<stack>` | Env-in-prefix partitioning so envs and stacks never collide in the one bucket. |

  `tfs validate` enforces this uniform rule; `make ci` runs it.

## CI/CD

Each stack is driven by a thin **per-stack caller**
(`.github/workflows/terraform-cicd-stack-<stack>.yml`, generated by `tfs create`)
that forwards to the shared **reusable workflow**
`.github/workflows/terraform-cicd-per-stack.yml`. The reusable workflow owns the
routing and delegates every cloud-touching terraform call to the composite action
[`.github/actions/terraform`](../.github/actions/terraform/README.md) (WIF auth +
init + plan/apply). See each stack's README for its trigger → env table.

## Tooling

| Tool | Role | Make target | Install |
|---|---|---|---|
| `terraform fmt` | Canonical formatter | `make fmt` / `make fmt-check` | bundled with terraform |
| `terraform validate` | Static check per env (post-init) | `make validate-<env>` | bundled with terraform |
| [`tfs`](./tfs/README.md) | Stack lifecycle: create / validate / gha-check / tf passthrough | `make create-stack` / `validate-backends` / `gha-check` | `uv tool install 'tfs @ ./infra/tfs'` (or `uv run --directory infra/tfs tfs …`) |
| [`tflint`](https://github.com/terraform-linters/tflint) | Lint + Google ruleset (`.tflint.hcl`) | `make lint` | `brew install tflint` then `tflint --init` |
| [`terraform-docs`](https://terraform-docs.io/) | Inject Inputs/Outputs tables into stack/module READMEs | `make docs` | `brew install terraform-docs` |
| [`trivy config`](https://trivy.dev/) | IaC security scan | `make security` | `brew install trivy` |

## See also

- [`../SETUP.md`](../SETUP.md) — **from-scratch runbook** (recreate the whole project step by step).
- [`stacks/webapp/README.md`](./stacks/webapp/README.md) — the Cloud Run + IAP stack (start here).
- [`modules/README.md`](./modules/README.md) — when/how to extract a module.
- [`bootstrap/README.md`](./bootstrap/README.md) — one-time GCP + GitHub setup.
- [`AUTH.md`](./AUTH.md) — the authn/authz model (TF Deployer + IAP access).
