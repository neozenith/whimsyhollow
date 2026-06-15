# The image build, modeled as a FIRST-CLASS node in the Terraform DAG (the fix for the
# apparent chicken-and-egg). `depends_on` the Artifact Registry repo, so Terraform
# orders: repo -> build (push image) -> Cloud Run (cloudrun.tf `depends_on`s this).
# Replaced only when local.app_src_hash changes — the AWS-Lambda zip-and-upload pattern
# (terraform_data + a source hash), applied to a container.
#
# Cloud Build does the Docker build REMOTELY, so the apply host needs gcloud + creds
# (CI has them via WIF; locally `tfs apply` uses your gcloud) but no Docker daemon.
# Skipped (count = 0) when var.container_image pins an explicit image — then no build
# is needed and Cloud Run uses the pin.
resource "terraform_data" "image" {
  count            = var.container_image == "" ? 1 : 0
  triggers_replace = local.app_src_hash

  provisioner "local-exec" {
    # Repo root, so backend/cloudbuild.yaml + the frontend source are in the build context.
    working_dir = "${path.module}/../../.."
    command     = "gcloud builds submit . --project ${local.project_id} --config backend/cloudbuild.yaml --substitutions=_IMAGE=${local.image_base}:${local.app_src_hash}"
  }

  depends_on = [google_artifact_registry_repository.app]
}
