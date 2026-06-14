locals {
  # SINGLE-PROJECT deployment: every environment shares this one project. (The
  # scaffold lineage derived this per-env as dbt-<env>-jaffleshop; here it is a
  # constant — dev/test/prod are partitions WITHIN whimsyhollow, not separate
  # projects.) See infra/README.md "Single-project namespacing".
  project_id = "whimsyhollow"

  # NAMESPACING — because all three environments live in the SAME project, every
  # env-scoped resource MUST carry the environment in its name or the three
  # deployments would collide on identical names. These locals are the single
  # source of those names; each resource references them instead of the bare
  # var.* base names. (Source relied on project isolation for uniqueness; this
  # repo relies on name isolation.)
  name           = "${var.service_name}-${var.environment}"                            # agentic-webapp-dev
  runtime_sa_id  = "${var.service_name}-run-${var.environment}"                        # agentic-webapp-run-dev (<=30 chars)
  repository_id  = "${var.repository_id}-${var.environment}"                           # agentic-webapp-dev
  assets_bucket  = "${local.project_id}-${var.service_name}-assets-${var.environment}" # whimsyhollow-agentic-webapp-assets-dev
  bq_dataset_id  = "${replace(var.service_name, "-", "_")}_${var.environment}"         # agentic_webapp_dev (BQ ids use underscores)
  firestore_name = "${var.service_name}-${var.environment}"                            # agentic-webapp-dev

  # IAP is enabled when a custom OAuth client is supplied — no-org projects require
  # one (ADR-0002), so its presence IS the on/off switch. In CI the client comes
  # from a per-environment GitHub secret (TF_VAR_iap_oauth_client_id); an env with
  # no such secret runs public. dev is public by design (no sensitive data, ADR-0003);
  # prod has the secret so IAP is on; test flips on the moment its secret is added.
  # var.enable_iap (default null) can still force a value for a one-off apply.
  iap_enabled = var.enable_iap != null ? var.enable_iap : (var.iap_oauth_client_id != "")
}

data "google_project" "this" {}

# APIs this stack needs. These are PROJECT-level resources, so in the single-project
# model all three env state files (dev/test/prod) co-own the same enablement on
# whimsyhollow. That is safe: enabling is idempotent (every apply converges to the
# same enabled=true), and disable_on_destroy=false means destroying one env's stack
# never yanks an API the other two envs (or anything else) still rely on.
resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iap" {
  service            = "iap.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "bigquery" {
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "aiplatform" {
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firestore" {
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}
