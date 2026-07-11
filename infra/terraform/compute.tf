data "oci_core_images" "always_free_ol" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  shape                    = var.shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

locals {
  cloud_init = templatefile("${path.module}/templates/cloud-init.yaml.tftpl", {
    api_image      = var.api_image
    web_image      = var.web_image
    pipeline_image = var.pipeline_image
    project_name   = var.project_name
    environment    = var.environment
  })
}

resource "oci_core_instance" "neo" {
  compartment_id      = var.compartment_ocid
  availability_domain = local.ad_name
  display_name        = "${local.name_prefix}-always-free"
  shape               = var.shape
  freeform_tags = merge(local.tags, {
    always_free = "true"
  })

  dynamic "shape_config" {
    for_each = local.is_a1 ? [1] : []
    content {
      ocpus         = var.ocpus
      memory_in_gbs = var.memory_in_gbs
    }
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public.id
    assign_public_ip = var.assign_public_ip
    display_name     = "${local.name_prefix}-vnic"
    hostname_label   = "nspo"
  }

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.always_free_ol.images[0].id
    boot_volume_size_in_gbs = var.boot_volume_size_in_gbs
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(local.cloud_init)
  }

  lifecycle {
    precondition {
      condition     = contains(tolist(local.always_free_shapes), var.shape)
      error_message = "Refusing non-Always-Free shape."
    }
  }
}
