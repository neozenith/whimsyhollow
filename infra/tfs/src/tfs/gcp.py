"""GCP guardrail — proves the active gcloud credentials can see the target
project before any state-touching terraform call.

Single-project model: there is ONE project (whimsyhollow) for every environment,
so the guardrail checks that one project regardless of env. (This must stay in
sync with local.project_id in stacks/webapp/main.tf.)"""

import logging
import subprocess

from tfs.errors import TFStackGCPConfigurationError

log = logging.getLogger(__name__)

# The single GCP project every environment deploys into. Keep in lockstep with
# local.project_id in the terraform stacks.
PROJECT_ID = "whimsyhollow"


def check_project(environment: str) -> None:
    """Prove you're authenticated against the single whimsyhollow project. Hard
    failure (no silent skip): if gcloud can't describe the project, stop. The
    environment arg is accepted for call-site symmetry but the project is constant
    — dev/test/prod are partitions within this one project."""
    project_id = PROJECT_ID
    log.debug("checking single-project guardrail for env=%s against project=%s", environment, project_id)
    try:
        result = subprocess.run(
            ["gcloud", "projects", "describe", project_id, "--format=value(projectId)"],
            text=True,
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as e:
        raise TFStackGCPConfigurationError("gcloud CLI not found on PATH — install the Google Cloud SDK") from e
    except subprocess.CalledProcessError as e:
        raise TFStackGCPConfigurationError(
            f"Cannot access project '{project_id}' with the active gcloud credentials.\n"
            f"  Authenticate first (e.g. `gcloud auth login` / ADC impersonation), then retry.\n"
            f"  gcloud said: {e.stderr.strip()}"
        ) from e
    log.debug("gcloud sees project: %s", result.stdout.strip())
