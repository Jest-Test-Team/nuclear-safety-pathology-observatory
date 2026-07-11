#!/usr/bin/env bash
# Plan OCI Neo changes (Terraform plan + optional Pulumi preview).
set -euo pipefail
# shellcheck source=common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_cmd terraform

: "${NSPO_API_IMAGE:?set NSPO_API_IMAGE}"
: "${NSPO_WEB_IMAGE:?set NSPO_WEB_IMAGE}"
: "${NSPO_PIPELINE_IMAGE:?set NSPO_PIPELINE_IMAGE}"
: "${TF_VAR_ssh_public_key:=${NSPO_SSH_PUBLIC_KEY:?set TF_VAR_ssh_public_key or NSPO_SSH_PUBLIC_KEY}}"
export TF_VAR_ssh_public_key

cd "${TF_DIR}"
echo_banner "terraform init"
terraform init -input=false

echo_banner "terraform plan"
# shellcheck disable=SC2046
terraform plan -input=false -out=tfplan $(eval tf_args)

echo_banner "terraform show"
terraform show -no-color tfplan | tee "${TF_DIR}/tfplan.txt"

if command -v pulumi >/dev/null 2>&1; then
  cd "${PULUMI_DIR}"
  [[ -d node_modules ]] || npm ci || npm install
  export PULUMI_CONFIG_PASSPHRASE="${PULUMI_CONFIG_PASSPHRASE:-nspo-local-dev}"
  pulumi stack select "${ENV_NAME}" 2>/dev/null || pulumi stack init "${ENV_NAME}"
  pulumi config set environment "${ENV_NAME}"
  pulumi config set apiImage "${NSPO_API_IMAGE}"
  pulumi config set webImage "${NSPO_WEB_IMAGE}"
  pulumi config set pipelineImage "${NSPO_PIPELINE_IMAGE}"
  pulumi config set skipApply true
  echo_banner "pulumi preview"
  pulumi preview --stack "${ENV_NAME}" --diff || true
fi

echo_banner "plan complete (tfplan written under infra/terraform)"
