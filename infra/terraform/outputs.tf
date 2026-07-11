output "environment" {
  value = var.environment
}

output "always_free" {
  value = {
    enforced  = true
    shape     = var.shape
    ocpus     = local.is_a1 ? var.ocpus : 1
    memory_gb = local.is_a1 ? var.memory_in_gbs : 1
    boot_gb   = var.boot_volume_size_in_gbs
    notes     = "Home-region Always Free only. No Container Instances, no LB stack."
  }
}

output "vcn_id" {
  value = oci_core_vcn.neo.id
}

output "subnet_id" {
  value = oci_core_subnet.public.id
}

output "compute_instance_id" {
  value = oci_core_instance.neo.id
}

output "public_ip" {
  value = try(oci_core_instance.neo.public_ip, null)
}

output "dashboard_url" {
  value = try("http://${oci_core_instance.neo.public_ip}/", null)
}

output "api_health_url" {
  value = try("http://${oci_core_instance.neo.public_ip}:8080/healthz", null)
}

output "ocir_repositories" {
  value = var.create_ocir_repos ? {
    api      = oci_artifacts_container_repository.api[0].display_name
    web      = oci_artifacts_container_repository.web[0].display_name
    pipeline = oci_artifacts_container_repository.pipeline[0].display_name
  } : {}
}

output "image_refs" {
  value = {
    api      = var.api_image
    web      = var.web_image
    pipeline = var.pipeline_image
  }
}
