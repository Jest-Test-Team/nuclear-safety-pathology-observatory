# OCI Neo deployment (Always Free only)

Deploy NSPO (`api`, `web`, `pipeline`) on Oracle Cloud **Always Free** resources only.

## Hard limits (enforced in Terraform)

| Resource | Allowed |
| --- | --- |
| Compute shape | `VM.Standard.A1.Flex` or `VM.Standard.E2.1.Micro` only |
| A1 capacity | ≤ **2 OCPU** and ≤ **12 GB** RAM |
| Boot volume | **47–200 GB** (default 50 GB) |
| Networking | VCN + public IP (no Load Balancer stack) |
| Runtime | Docker Compose on the VM (not Container Instances) |
| Region | Tenancy **home region** |

Paid shapes, Container Instances, and LB stacks are rejected by variable validation / `check` blocks.

## Layout

```text
infra/terraform/     Always Free OCI resources
infra/pulumi/        Pulumi wrapper (image tags → terraform)
scripts/oci/         validate / plan / apply
```

## Prerequisites

1. OCI Always Free / free-tier tenancy (home region)
2. API key (user OCID, fingerprint, PEM) + SSH public key
3. Terraform ≥ 1.6, Node 22+
4. **linux/arm64** images from the `release` workflow when using A1

## Local usage

```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
# fill tenancy/user/fingerprint/compartment/private_key_path/ssh_public_key

export NSPO_API_IMAGE=...        # arm64 for A1
export NSPO_WEB_IMAGE=...
export NSPO_PIPELINE_IMAGE=...
export TF_VAR_ssh_public_key="$(cat ~/.ssh/id_ed25519.pub)"

./scripts/oci/validate.sh
./scripts/oci/plan.sh
./scripts/oci/apply.sh
```

```bash
make oci-validate && make oci-plan && make oci-apply
```

## GitHub Actions

| Workflow | Purpose |
| --- | --- |
| `release.yml` | Build **linux/arm64** images, push GHCR (+ optional OCIR), GitHub Release |
| `deploy-oci.yml` | validate / plan / apply Always Free Neo VM |

### Required secrets (deploy)

- `OCI_TENANCY_OCID`, `OCI_USER_OCID`, `OCI_FINGERPRINT`, `OCI_API_PRIVATE_KEY`
- `OCI_REGION` (must be home region), `OCI_COMPARTMENT_OCID`
- `OCI_SSH_PUBLIC_KEY`
- `PULUMI_CONFIG_PASSPHRASE` (optional)

## Safety note

Deployed findings remain research review candidates (`requires-expert-review`). This stack does not add facility-control or emergency alerting capability.
