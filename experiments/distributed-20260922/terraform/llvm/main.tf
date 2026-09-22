# The LLVM parity pair of 2026-09-22 (yohimik/llvm-project, branch dispat-gce
# at 952c2de4, .ci/dispat/gce/REPORT.md attempts 8 and 9): an e2-standard-4
# orchestrator and two n2-custom-14-49152 workers in one zone. The baseline of
# the pair runs on the second worker alone after the distributed run, so no
# extra node is needed. Every node deletes itself after `max_run_seconds`.
#
#   terraform init
#   terraform apply -var project=dispat
#   ../../scripts/llvm/run.sh
#   terraform destroy -var project=dispat
terraform {
  required_version = ">= 1.6"
  required_providers {
    google = { source = "hashicorp/google", version = ">= 6.0" }
    tls    = { source = "hashicorp/tls", version = ">= 4.0" }
    random = { source = "hashicorp/random", version = ">= 3.5" }
    local  = { source = "hashicorp/local", version = ">= 2.4" }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

locals {
  node_user     = "dispat"
  operator_line = "${local.node_user}:${trimspace(tls_private_key.operator.public_key_openssh)} operator"
  mailbox_line  = "${local.node_user}:${trimspace(tls_private_key.mailbox.public_key_openssh)} mailbox"
  common_metadata = {
    "node-user"         = local.node_user
    "dispat-dockerfile" = file("${path.module}/../../docker/dispat/Dockerfile")
    "node-dockerfile"   = file("${path.module}/../../docker/llvm-node/Dockerfile")
    "dispat-commit"     = var.dispat_commit
    "dispat-version"    = var.dispat_version
    "apt-snapshot"      = var.apt_snapshot
  }
  startup = file("${path.module}/../../scripts/llvm/node-startup.sh")
  workers = { w1 = "${var.name_prefix}-w1", w2 = "${var.name_prefix}-w2" }
}

resource "google_compute_network" "net" {
  name                    = "${var.name_prefix}-net"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${var.name_prefix}-subnet"
  network       = google_compute_network.net.id
  region        = var.region
  ip_cidr_range = var.subnet_cidr
}

resource "google_compute_firewall" "internal" {
  name    = "${var.name_prefix}-internal"
  network = google_compute_network.net.name
  allow { protocol = "tcp" }
  allow { protocol = "udp" }
  allow { protocol = "icmp" }
  source_ranges = [var.subnet_cidr]
}

resource "google_compute_firewall" "ssh" {
  name    = "${var.name_prefix}-ssh"
  network = google_compute_network.net.name
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = var.ssh_source_ranges
}

resource "tls_private_key" "operator" { algorithm = "ED25519" }
resource "tls_private_key" "mailbox" { algorithm = "ED25519" }
resource "random_id" "execution_secret" { byte_length = 32 }

module "orchestrator" {
  source          = "../modules/gce-node"
  name            = "${var.name_prefix}-orch"
  machine_type    = var.orchestrator_machine_type
  zone            = var.zone
  image           = var.image
  disk_gb         = var.orchestrator_disk_gb
  max_run_seconds = var.max_run_seconds
  subnetwork      = google_compute_subnetwork.subnet.id
  startup_script  = local.startup
  ssh_keys        = "${local.operator_line}\n${local.mailbox_line}"
  metadata        = merge(local.common_metadata, { "node-role" = "orchestrator" })
  labels          = { purpose = "dispat-llvm-experiment", role = "orchestrator" }
}

module "worker" {
  for_each        = local.workers
  source          = "../modules/gce-node"
  name            = each.value
  machine_type    = var.worker_machine_type
  zone            = var.zone
  image           = var.image
  disk_gb         = var.worker_disk_gb
  max_run_seconds = var.max_run_seconds
  subnetwork      = google_compute_subnetwork.subnet.id
  startup_script  = local.startup
  ssh_keys        = local.operator_line
  metadata        = merge(local.common_metadata, { "node-role" = "worker", "node-name" = each.key })
  labels          = { purpose = "dispat-llvm-experiment", role = "worker" }
}

resource "local_sensitive_file" "operator_key" {
  content         = tls_private_key.operator.private_key_openssh
  filename        = "${path.module}/.secrets/operator"
  file_permission = "0600"
}
resource "local_sensitive_file" "mailbox_key" {
  content         = tls_private_key.mailbox.private_key_openssh
  filename        = "${path.module}/.secrets/mailbox_key"
  file_permission = "0600"
}
resource "local_sensitive_file" "execution_secret" {
  content         = random_id.execution_secret.hex
  filename        = "${path.module}/.secrets/execution_secret"
  file_permission = "0600"
}

output "nodes" {
  value = {
    orchestrator = { name = module.orchestrator.name, zone = module.orchestrator.zone, internal_ip = module.orchestrator.internal_ip, external_ip = module.orchestrator.external_ip }
    w1           = { name = module.worker["w1"].name, zone = module.worker["w1"].zone, internal_ip = module.worker["w1"].internal_ip, external_ip = module.worker["w1"].external_ip }
    w2           = { name = module.worker["w2"].name, zone = module.worker["w2"].zone, internal_ip = module.worker["w2"].internal_ip, external_ip = module.worker["w2"].external_ip }
  }
}
output "node_user" { value = local.node_user }
output "project" { value = var.project }
