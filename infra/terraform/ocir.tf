resource "oci_artifacts_container_repository" "api" {
  count          = var.create_ocir_repos ? 1 : 0
  compartment_id = var.compartment_ocid
  display_name   = "${var.project_name}/api"
  is_public      = false
  freeform_tags  = local.tags
}

resource "oci_artifacts_container_repository" "web" {
  count          = var.create_ocir_repos ? 1 : 0
  compartment_id = var.compartment_ocid
  display_name   = "${var.project_name}/web"
  is_public      = false
  freeform_tags  = local.tags
}

resource "oci_artifacts_container_repository" "pipeline" {
  count          = var.create_ocir_repos ? 1 : 0
  compartment_id = var.compartment_ocid
  display_name   = "${var.project_name}/pipeline"
  is_public      = false
  freeform_tags  = local.tags
}
