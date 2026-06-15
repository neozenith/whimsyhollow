# The Docker repo the app image is pushed to — a FIRST-CLASS stack resource so the
# Terraform dependency graph sequences it correctly: repo -> image build -> Cloud Run
# (see build.tf + cloudrun.tf `depends_on`). There is no chicken-and-egg once the build
# is a node in the DAG that depends on the repo; the earlier cycle only existed because
# the build was a CI shell step OUTSIDE the graph.
resource "google_artifact_registry_repository" "app" {
  location      = var.region
  repository_id = local.repository_id # whimsyhollow-<env>
  format        = "DOCKER"
  description   = "Container images for the ${local.name} Cloud Run service."

  depends_on = [google_project_service.artifactregistry]
}

# Cloud Run pulls the image as the runtime SA — give it read on the repo.
resource "google_artifact_registry_repository_iam_member" "runtime_reader" {
  location   = google_artifact_registry_repository.app.location
  repository = google_artifact_registry_repository.app.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.runtime.email}"
}

locals {
  # Fully-qualified image base: <region>-docker.pkg.dev/<project>/<repo>/<image>.
  image_base = "${var.region}-docker.pkg.dev/${local.project_id}/${local.repository_id}/${local.name}"

  # Content-addressed tag: a hash of the app source (backend/ + frontend/, excluding
  # generated dirs). It changes only when the app actually changes, so the build
  # resource (build.tf) rebuilds and Cloud Run gets a new revision only on a real code
  # change — the container analogue of AWS Lambda's source_code_hash.
  app_src_hash = substr(sha1(join("", [
    for f in sort(flatten([
      for d in ["backend", "frontend"] : [
        for p in fileset("${path.module}/../../../${d}", "**") :
        filesha1("${path.module}/../../../${d}/${p}")
        if length(regexall("(^|/)(node_modules|dist|[.]venv|__pycache__|[.]terraform)(/|$)", p)) == 0
      ]
    ])) : f
  ])), 0, 12)

  # The image Cloud Run runs: the freshly-built source-hash image by default;
  # var.container_image can pin a specific tag instead (e.g. a rollback).
  app_image = var.container_image != "" ? var.container_image : "${local.image_base}:${local.app_src_hash}"
}
