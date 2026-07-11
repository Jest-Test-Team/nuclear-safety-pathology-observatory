#!/usr/bin/env bash
# Validate Terraform + Pulumi project for OCI Neo.
set -euo pipefail
# shellcheck source=common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_cmd node
require_cmd npm

# Dummy auth values satisfy required variables during validate-only runs.
export TF_VAR_tenancy_ocid="${TF_VAR_tenancy_ocid:-ocid1.tenancy.oc1..validate}"
export TF_VAR_user_ocid="${TF_VAR_user_ocid:-ocid1.user.oc1..validate}"
export TF_VAR_fingerprint="${TF_VAR_fingerprint:-https://example.invalid/fingerprint}"
export TF_VAR_region="${TF_VAR_region:-ap-singapore-1}"
export TF_VAR_compartment_ocid="${TF_VAR_compartment_ocid:-ocid1.compartment.oc1..validate}"
export TF_VAR_private_key_path="${TF_VAR_private_key_path:-/dev/null}"
export TF_VAR_ssh_public_key="${TF_VAR_ssh_public_key:-ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIValidateOnlyKey nspo-validate}"

if command -v terraform >/dev/null 2>&1; then
  echo_banner "terraform fmt (check)"
  cd "${TF_DIR}"
  terraform fmt -check -recursive

  echo_banner "terraform init"
  terraform init -input=false -backend=false

  echo_banner "terraform validate"
  terraform validate
else
  echo_banner "terraform not installed; skipping fmt/init/validate (install Terraform >= 1.6 or rely on CI)"
fi

echo_banner "pulumi TypeScript build"
cd "${PULUMI_DIR}"
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
npm run build

if command -v pulumi >/dev/null 2>&1; then
  export PULUMI_CONFIG_PASSPHRASE="${PULUMI_CONFIG_PASSPHRASE:-nspo-local-dev}"
  pulumi stack select "${ENV_NAME}" 2>/dev/null || pulumi stack init "${ENV_NAME}"
  pulumi config set environment "${ENV_NAME}"
  pulumi config set apiImage "${NSPO_API_IMAGE:-ghcr.io/example/nspo-api:validate}"
  pulumi config set webImage "${NSPO_WEB_IMAGE:-ghcr.io/example/nspo-web:validate}"
  pulumi config set pipelineImage "${NSPO_PIPELINE_IMAGE:-ghcr.io/example/nspo-pipeline:validate}"
  pulumi config set skipApply true
  echo "pulumi stack ${ENV_NAME} configured (skipApply=true)"
fi

echo_banner "validate complete"
