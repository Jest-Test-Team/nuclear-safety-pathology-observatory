#!/usr/bin/env bash
# Shared helpers for OCI Neo Terraform + Pulumi workflows.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TF_DIR="${ROOT_DIR}/infra/terraform"
PULUMI_DIR="${ROOT_DIR}/infra/pulumi"
ENV_NAME="${NSPO_OCI_ENV:-neo}"
VAR_FILE="${TF_VAR_FILE:-environments/${ENV_NAME}.tfvars}"

export TF_IN_AUTOMATION="${TF_IN_AUTOMATION:-1}"
export TF_INPUT="${TF_INPUT:-0}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "missing required command: $1" >&2
    exit 1
  }
}

tf_args() {
  local args=()
  if [[ -f "${TF_DIR}/${VAR_FILE}" ]]; then
    args+=(-var-file="${VAR_FILE}")
  fi
  if [[ -n "${NSPO_API_IMAGE:-}" ]]; then
    args+=(-var="api_image=${NSPO_API_IMAGE}")
  fi
  if [[ -n "${NSPO_WEB_IMAGE:-}" ]]; then
    args+=(-var="web_image=${NSPO_WEB_IMAGE}")
  fi
  if [[ -n "${NSPO_PIPELINE_IMAGE:-}" ]]; then
    args+=(-var="pipeline_image=${NSPO_PIPELINE_IMAGE}")
  fi
  if [[ -n "${TF_VAR_ssh_public_key:-}" ]]; then
    : # already exported for Terraform
  elif [[ -n "${NSPO_SSH_PUBLIC_KEY:-}" ]]; then
    export TF_VAR_ssh_public_key="${NSPO_SSH_PUBLIC_KEY}"
  fi
  printf '%q ' "${args[@]}"
}

echo_banner() {
  echo
  echo "==> $*"
}
