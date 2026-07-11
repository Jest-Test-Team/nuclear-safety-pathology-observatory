# Always Free tier hard limits (home region only).
# Docs: https://docs.oracle.com/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
#
# Ampere A1 (free-tier equivalent continuous usage): <= 2 OCPU and <= 12 GB RAM
# AMD Micro: VM.Standard.E2.1.Micro only (up to 2 instances)
# Block volume Always Free pool: 200 GB (boot volumes count)

locals {
  always_free_shapes = toset([
    "VM.Standard.A1.Flex",
    "VM.Standard.E2.1.Micro",
  ])

  always_free_a1_max_ocpus    = 2
  always_free_a1_max_memory   = 12
  always_free_boot_min_gb     = 47
  always_free_boot_max_gb     = 200
  always_free_boot_default_gb = 50

  is_a1    = var.shape == "VM.Standard.A1.Flex"
  is_micro = var.shape == "VM.Standard.E2.1.Micro"
}

check "always_free_shape_only" {
  assert {
    condition     = contains(tolist(local.always_free_shapes), var.shape)
    error_message = "NSPO OCI Neo is Always Free only. Allowed shapes: VM.Standard.A1.Flex, VM.Standard.E2.1.Micro. Container Instances and paid shapes are forbidden."
  }
}

check "always_free_a1_limits" {
  assert {
    condition = !local.is_a1 || (
      var.ocpus <= local.always_free_a1_max_ocpus &&
      var.memory_in_gbs <= local.always_free_a1_max_memory &&
      var.ocpus >= 1 &&
      var.memory_in_gbs >= 1
    )
    error_message = "Always Free A1 limit exceeded: ocpus must be 1..2 and memory_in_gbs must be 1..12."
  }
}

check "always_free_boot_volume" {
  assert {
    condition = (
      var.boot_volume_size_in_gbs >= local.always_free_boot_min_gb &&
      var.boot_volume_size_in_gbs <= local.always_free_boot_max_gb
    )
    error_message = "Boot volume must be 47..200 GB to stay within Always Free block storage."
  }
}

check "always_free_no_paid_lb" {
  assert {
    condition     = var.enable_load_balancer == false
    error_message = "Paid/complex LB stacks are disabled. Always Free Neo uses the instance public IP only."
  }
}
