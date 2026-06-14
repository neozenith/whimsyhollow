#!/usr/bin/env bash
# Bootstrap the single GCP project (whimsyhollow).
#
# In the single-project model there is exactly one project to bootstrap, so this
# is a thin wrapper around bootstrap_project.sh kept for Makefile-target stability
# (`make bootstrap`). Assumes you are already authenticated (CLOUDSDK_* env vars
# set, or `gcloud auth login` completed). Authentication is NOT performed here.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./config.sh
source "${SCRIPT_DIR}/config.sh"

"${SCRIPT_DIR}/bootstrap_project.sh"

cat <<'EOF'

==> Project bootstrapped.

Next step: configure the dev/test/prod GitHub Environments with the variables
printed above (all three point at the SAME WIF provider + deployer SA, since they
deploy into the one project). Either set them by hand in the GitHub UI, or run:

    ./infra/bootstrap/bootstrap_github.sh

EOF
