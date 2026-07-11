data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  ad_name     = data.oci_identity_availability_domains.ads.availability_domains[var.availability_domain_number - 1].name
  tags = merge(var.freeform_tags, {
    environment = var.environment
  })
}

resource "oci_core_vcn" "neo" {
  compartment_id = var.compartment_ocid
  display_name   = "${local.name_prefix}-vcn"
  cidr_blocks    = [var.vcn_cidr]
  dns_label      = replace("${var.project_name}${var.environment}", "-", "")
  freeform_tags  = local.tags
}

resource "oci_core_internet_gateway" "neo" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.neo.id
  display_name   = "${local.name_prefix}-igw"
  enabled        = true
  freeform_tags  = local.tags
}

resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.neo.id
  display_name   = "${local.name_prefix}-public-rt"
  freeform_tags  = local.tags

  route_rules {
    network_entity_id = oci_core_internet_gateway.neo.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

resource "oci_core_security_list" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.neo.id
  display_name   = "${local.name_prefix}-public-sl"
  freeform_tags  = local.tags

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 8080
      max = 8080
    }
  }
}

resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.neo.id
  display_name               = "${local.name_prefix}-public"
  cidr_block                 = var.subnet_cidr
  route_table_id             = oci_core_route_table.public.id
  security_list_ids          = [oci_core_security_list.public.id]
  prohibit_public_ip_on_vnic = false
  dns_label                  = "public"
  freeform_tags              = local.tags
}
