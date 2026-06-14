# `infra/bootstrap/`

One-time scripts that prepare the single `whimsyhollow` GCP project so **this
repo's** Terraform can manage a Cloud Run + IAP webapp from GitHub Actions. The
project is bootstrapped once; dev/test/prod are partitions within it. Every
script is idempotent — re-running is safe.

## Quickstart

```bash
# 1. Bootstrap GCP (the whimsyhollow project)
./infra/bootstrap/bootstrap_all.sh

# 2. Bootstrap GitHub Environments + variables
./infra/bootstrap/bootstrap_github.sh
```

Or run the GCP step directly (takes no arguments — it reads `config.sh`):

```bash
./infra/bootstrap/bootstrap_project.sh
```

It prints the two values to copy into each **GitHub Environment** (Settings →
Environments → `dev`/`test`/`prod`). All three environments get the **same**
two values:

```
WIF_PROVIDER  = projects/<number>/locations/global/workloadIdentityPools/github-pool/providers/whimsyhollow-provider
TF_SA         = whimsyhollow-deployer@whimsyhollow.iam.gserviceaccount.com
```

`bootstrap_github.sh` writes both vars to all three environments via the GitHub
API; the manual UI route is the fallback. Per-env isolation is enforced by
GitHub Environment protection rules + the per-env terraform state prefix, not by
distinct credentials.

## What this creates

This repo owns the `whimsyhollow` project, so the bootstrap creates one of each
project-level resource (no sharing, no reuse from another platform):

| # | Resource | Action | Notes |
|---|---|---|---|
| 1 | APIs (`run`, `iap`, + base set) | enable | idempotent / additive |
| 2 | `whimsyhollow-tfstate` bucket | **create** | one bucket; state partitioned by env-in-prefix (`terraform/state/<env>/webapp`) |
| 3 | `whimsyhollow-deployer` SA | **create** | the single CI deployer identity |
| 4 | `github-pool` WIF pool | **create** | one pool for the project |
| 5 | `whimsyhollow-provider` OIDC provider | **create** | scoped to `neozenith/whimsyhollow` |
| 6 | `workloadIdentityUser` binding | **create** | binds this repo's principalSet to the deployer SA |

## Prerequisites

1. The `whimsyhollow` GCP project already exists with billing enabled.
2. The caller is authenticated to gcloud with rights to enable services, create
   service accounts, grant `roles/owner`, and create WIF providers on the project.
3. `gh` CLI installed + authenticated with repo-admin on `${GITHUB_REPO}` (needed
   by `bootstrap_github.sh`).

The scripts deliberately **do not** authenticate — they assume the caller already
has credentials.

## IAP one-time manual step (no-org project)

The `whimsyhollow` project belongs to a Gmail account with **no GCP
organization**. IAP's OAuth consent screen for *external* user type cannot be
created via Terraform (`google_iap_brand` only supports org-internal brands).
Before the first apply of the `webapp` stack, configure the consent screen once
in the Console:

> APIs & Services → OAuth consent screen → User type **External** → fill app name
> + support email → Save. (No need to add scopes or publish for IAP to work with
> your own Google account as a test user / owner.)

This is a genuine manual prerequisite, not an optional step — see
[`../stacks/webapp/README.md`](../stacks/webapp/README.md).

## Scripts

| Script | Purpose |
|---|---|
| `config.sh` | Shared constants: `PROJECT_ID=whimsyhollow`, `TF_STATE_BUCKET=whimsyhollow-tfstate`, `TF_SA_NAME=whimsyhollow-deployer`, `WIF_POOL_ID=github-pool`, `WIF_PROVIDER_ID=whimsyhollow-provider`, `GITHUB_REPO=neozenith/whimsyhollow`, and an `ENVIRONMENTS=(dev test prod)` array. Sourced by the others. |
| `bootstrap_project.sh` | Sets up the project-level steps for the single project. Takes **no arguments** (reads `config.sh`). |
| `bootstrap_all.sh` | Calls `bootstrap_project.sh` once for the `whimsyhollow` project. |
| `bootstrap_github.sh` | Creates the GitHub Environments and writes the same `WIF_PROVIDER` + `TF_SA` to all three. Run **after** `bootstrap_all.sh`. |

## Overriding defaults

The scripts honour environment variables so one-off overrides don't require
editing `config.sh`:

```bash
GITHUB_REPO=neozenith/some-fork ./infra/bootstrap/bootstrap_all.sh
TF_STATE_LOCATION=us-central1   ./infra/bootstrap/bootstrap_project.sh
```
