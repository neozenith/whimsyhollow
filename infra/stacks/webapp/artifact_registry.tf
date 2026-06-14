# The Docker repo the app image is pushed to is FOUNDATIONAL plumbing created once by
# infra/bootstrap (gcloud), NOT by this per-deploy stack — that's what removes the
# build-vs-terraform chicken-and-egg (CI pushes the image before `tfs apply` runs).
# Here we only reference it (read-only) to grant the runtime SA pull access.
data "google_artifact_registry_repository" "app" {
  location      = var.region
  repository_id = local.repository_id # whimsyhollow-<env>, created by bootstrap_project.sh
}

# Cloud Run pulls the image as the runtime SA — give it read on the repo.
resource "google_artifact_registry_repository_iam_member" "runtime_reader" {
  location   = data.google_artifact_registry_repository.app.location
  repository = data.google_artifact_registry_repository.app.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.runtime.email}"
}

locals {
  # Convenience: the fully-qualified image base. Append :<tag> when pushing.
  #   <region>-docker.pkg.dev/<project>/<repo-with-env>/<image-with-env>
  # Both the repo and image components carry the env (local.repository_id / local.name)
  # so they stay unique in the single project AND match the CI image-path formatter.
  image_base = "${var.region}-docker.pkg.dev/${local.project_id}/${local.repository_id}/${local.name}"
}
