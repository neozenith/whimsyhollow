# All resources here are gated on local.iap_enabled. When IAP is off, the service is
# made public in cloudrun.tf (google_cloud_run_v2_service_iam_member.public_invoker)
# and none of this is created.

# Force-create the IAP service agent now, so the run.invoker grant below has a
# member that already exists. Otherwise GCP creates the agent lazily on first IAP
# use and the first apply races / fails with "member does not exist". Requires
# the google-beta provider.
resource "google_project_service_identity" "iap" {
  count    = local.iap_enabled ? 1 : 0
  provider = google-beta
  service  = "iap.googleapis.com"

  depends_on = [google_project_service.iap]
}

# IAP invokes Cloud Run AS the IAP service agent, so the AGENT (not the end user)
# needs run.invoker on the service. This is the inner hop of the two-hop auth.
resource "google_cloud_run_v2_service_iam_member" "iap_invoker" {
  count    = local.iap_enabled ? 1 : 0
  name     = google_cloud_run_v2_service.app.name
  location = google_cloud_run_v2_service.app.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_project_service_identity.iap[0].email}"
}

# Attach a CUSTOM OAuth client to IAP. No-org projects can't use IAP's
# Google-managed OAuth client, so without this IAP returns 502 "Empty OAuth
# client". The client itself is created manually in the Console (no API exists for
# OAuth-client creation in no-org projects); its id/secret are passed in as vars.
# Only created when IAP is on AND a client id was supplied.
resource "google_iap_settings" "webapp" {
  count = local.iap_enabled && var.iap_oauth_client_id != "" ? 1 : 0
  name  = "projects/${data.google_project.this.number}/iap_web/cloud_run-${var.region}/services/${google_cloud_run_v2_service.app.name}"

  access_settings {
    oauth_settings {
      client_id     = var.iap_oauth_client_id
      client_secret = var.iap_oauth_client_secret
    }
  }
}

# The actual allow-list: only these principals may pass through IAP (see
# local.iap_principals, built from var.iap_members + var.iap_member_groups). This is
# the outer hop — it governs who the human-facing IAP layer will admit.
#
# count (not for_each): iap_principals is sensitive, and Terraform forbids sensitive
# values as for_each keys (they'd be exposed in the resource address). nonsensitive()
# wraps only the COUNT — it reveals how MANY principals there are, never who.
resource "google_iap_web_cloud_run_service_iam_member" "accessors" {
  count = local.iap_enabled ? nonsensitive(length(local.iap_principals)) : 0

  project                = local.project_id
  location               = google_cloud_run_v2_service.app.location
  cloud_run_service_name = google_cloud_run_v2_service.app.name
  role                   = "roles/iap.httpsResourceAccessor"
  member                 = local.iap_principals[count.index]

  depends_on = [google_project_service.iap]
}
