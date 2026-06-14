#!/usr/bin/env bash
# Shared configuration for the bootstrap scripts.
# Source this file from other scripts; do not execute it directly.
#
# SINGLE-PROJECT model: everything lives in ONE GCP project (whimsyhollow).
# dev/test/prod are NOT separate projects — they are partitions within this one
# project (state by GCS prefix, resources by -<env> name suffix). So bootstrap
# provisions ONE of each project-level primitive (state bucket, deployer SA, WIF
# provider); the three GitHub Environments all point at that single set.

# GitHub repo allowed to impersonate the deployer service account via WIF.
GITHUB_REPO="${GITHUB_REPO:-neozenith/whimsyhollow}"

# The single GCP project everything deploys into. Must match local.project_id in
# the terraform stacks and PROJECT_ID in infra/tfs/src/tfs/gcp.py.
PROJECT_ID="${PROJECT_ID:-whimsyhollow}"

# GCS location for the single Terraform state bucket.
TF_STATE_LOCATION="${TF_STATE_LOCATION:-australia-southeast1}"

# The single tfstate bucket. dev/test/prod state is partitioned WITHIN it by the
# GCS prefix terraform/state/<env>/<stack> (see infra/config.yml + backends/*.config).
TF_STATE_BUCKET="${TF_STATE_BUCKET:-whimsyhollow-tfstate}"

# Resource naming for the CI deployer identity (one SA, one pool, one provider).
TF_SA_NAME="${TF_SA_NAME:-whimsyhollow-deployer}"
WIF_POOL_ID="${WIF_POOL_ID:-github-pool}"
WIF_PROVIDER_ID="${WIF_PROVIDER_ID:-whimsyhollow-provider}"

# The environments that get a GitHub Environment (state/resource partitions, all in
# the one project). Order: dev first (cheapest to fail in).
ENVIRONMENTS=(dev test prod)
