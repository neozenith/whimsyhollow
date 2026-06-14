locals {
  # SINGLE-PROJECT model: one project for every environment. dev/test/prod are
  # partitions within it (state by GCS prefix; resources by -<env> name suffix),
  # NOT separate projects. Must match the project bootstrapped by
  # infra/bootstrap/bootstrap_project.sh.
  project_id = "whimsyhollow"

  # Because every env shares this project, namespace each env-scoped resource with
  # the environment to avoid collisions. Add names here as the stack grows, e.g.:
  #   name = "${var.environment}-myresource"
}

# Smoke test: proves the deployer SA can read its own project. Replace / extend
# with real resources (or module calls) as the stack grows.
data "google_project" "this" {}

output "project_id" {
  value = data.google_project.this.project_id
}

output "project_number" {
  value = data.google_project.this.number
}
