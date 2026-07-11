#!/usr/bin/env bash
# Apply OCI Neo infrastructure (Terraform apply; Pulumi up mirrors image config).
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

if [[ ! -f tfplan ]]; then
  echo_banner "no tfplan found; generating plan"
  # shellcheck disable=SC2046
  terraform plan -input=false -out=tfplan $(eval tf_args)
fi

echo_banner "terraform apply"
terraform apply -input=false tfplan

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
  pulumi config set autoApprove true
  echo_banner "pulumi up (config sync; terraform already applied)"
  pulumi up --stack "${ENV_NAME}" --yes --skip-preview || true
fi

echo_banner "apply complete"
terraform -chdir="${TF_DIR}" output -json > "${TF_DIR}/outputs.json" || true
cat "${TF_DIR}/outputs.json" 2>/dev/null || terraform -chdir="${TF_DIR}" output
