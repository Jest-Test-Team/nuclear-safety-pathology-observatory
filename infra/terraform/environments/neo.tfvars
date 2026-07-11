# Neo Always Free defaults (non-secret). Auth via TF_VAR_* / terraform.tfvars.
environment             = "neo"
project_name            = "nspo"
vcn_cidr                = "10.42.0.0/16"
subnet_cidr             = "10.42.1.0/24"
shape                   = "VM.Standard.A1.Flex"
ocpus                   = 1
memory_in_gbs           = 6
boot_volume_size_in_gbs = 50
create_ocir_repos       = false
assign_public_ip        = true
enable_load_balancer    = false

# Overridden by NSPO_*_IMAGE / -var in scripts and GHA (use linux/arm64 tags for A1).
api_image      = "ghcr.io/example/nspo-api:neo"
web_image      = "ghcr.io/example/nspo-web:neo"
pipeline_image = "ghcr.io/example/nspo-pipeline:neo"
