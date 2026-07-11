variable "tenancy_ocid" {
  type        = string
  description = "OCI tenancy OCID (Always Free resources must be in the home region)"
}

variable "user_ocid" {
  type        = string
  description = "OCI user OCID used for API access"
}

variable "fingerprint" {
  type        = string
  description = "API key fingerprint"
}

variable "private_key_path" {
  type        = string
  description = "Path to PEM private key (local runs). Leave empty when private_key is set."
  default     = ""
}

variable "private_key" {
  type        = string
  description = "PEM private key contents (CI). Prefer over private_key_path in GitHub Actions."
  default     = ""
  sensitive   = true
}

variable "region" {
  type        = string
  description = "OCI home region (Always Free compute is home-region only)"
}

variable "compartment_ocid" {
  type        = string
  description = "Target compartment OCID for Neo environment"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "neo"
}

variable "project_name" {
  type    = string
  default = "nspo"
}

variable "vcn_cidr" {
  type    = string
  default = "10.42.0.0/16"
}

variable "subnet_cidr" {
  type    = string
  default = "10.42.1.0/24"
}

variable "availability_domain_number" {
  type        = number
  description = "1-based AD index within the region"
  default     = 1
}

variable "shape" {
  type        = string
  description = "Always Free compute shape only"
  default     = "VM.Standard.A1.Flex"

  validation {
    condition     = contains(["VM.Standard.A1.Flex", "VM.Standard.E2.1.Micro"], var.shape)
    error_message = "Only Always Free shapes are allowed: VM.Standard.A1.Flex or VM.Standard.E2.1.Micro."
  }
}

variable "ocpus" {
  type        = number
  description = "A1 OCPUs (ignored for E2.1.Micro). Always Free cap: 2."
  default     = 1

  validation {
    condition     = var.ocpus >= 1 && var.ocpus <= 2
    error_message = "ocpus must be between 1 and 2 for Always Free A1."
  }
}

variable "memory_in_gbs" {
  type        = number
  description = "A1 memory GB (ignored for E2.1.Micro). Always Free cap: 12."
  default     = 6

  validation {
    condition     = var.memory_in_gbs >= 1 && var.memory_in_gbs <= 12
    error_message = "memory_in_gbs must be between 1 and 12 for Always Free A1."
  }
}

variable "boot_volume_size_in_gbs" {
  type        = number
  description = "Boot volume size (Always Free pool is 200 GB total; min 47 GB)"
  default     = 50

  validation {
    condition     = var.boot_volume_size_in_gbs >= 47 && var.boot_volume_size_in_gbs <= 200
    error_message = "boot_volume_size_in_gbs must be 47..200 for Always Free."
  }
}

variable "ssh_public_key" {
  type        = string
  description = "SSH public key for the Always Free compute instance"
}

variable "api_image" {
  type        = string
  description = "Fully-qualified container image for the API (prefer linux/arm64 for A1)"
}

variable "web_image" {
  type        = string
  description = "Fully-qualified container image for the web dashboard"
}

variable "pipeline_image" {
  type        = string
  description = "Fully-qualified container image for the analysis pipeline"
}

variable "create_ocir_repos" {
  type        = bool
  description = "Create OCIR repositories (uses Always Free object storage quota). Prefer GHCR when possible."
  default     = false
}

variable "assign_public_ip" {
  type    = bool
  default = true
}

variable "enable_load_balancer" {
  type        = bool
  description = "Must remain false: Neo Always Free uses the instance public IP (no LB stack)."
  default     = false

  validation {
    condition     = var.enable_load_balancer == false
    error_message = "enable_load_balancer must be false for Always Free Neo."
  }
}

variable "freeform_tags" {
  type = map(string)
  default = {
    project     = "nspo"
    mode        = "research-public-data-only"
    cost_center = "always-free"
  }
}
