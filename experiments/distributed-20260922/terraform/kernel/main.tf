# The kernel farm parity experiment of 2026-09-22 (round 2 of
# yohimik/linux-build-test, branch codex/kernel-parity at c699bf3d): a
# c3-standard-22 that starts the release and builds, a t2d-standard-8 worker
# that builds one cell per group, and optionally a second c3-standard-22 that
# builds every cell alone (the same-hardware pair). Every node deletes itself
# after `max_run_seconds`.
#
#   terraform init
#   terraform apply -var project=dispat-linux-parity
#   ../../scripts/kernel/run.sh        # from this directory, after apply
#   terraform destroy -var project=dispat-linux-parity
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
  node_user = "dispat"
  # Two keys: the operator's, which run.sh uses to reach every node, and the
  # mailbox key, which the worker uses to reach the orchestrator's mailbox.
  # The orchestrator authorises both; the worker only the operator's.
  operator_line = "${local.node_user}:${trimspace(tls_private_key.operator.public_key_openssh)} operator"
  mailbox_line  = "${local.node_user}:${trimspace(tls_private_key.mailbox.public_key_openssh)} mailbox"
  common_metadata = {
    "node-user"         = local.node_user
    "dispat-dockerfile" = file("${path.module}/../../docker/dispat/Dockerfile")
    "node-dockerfile"   = file("${path.module}/../../docker/kernel-node/Dockerfile")
    "dispat-commit"     = var.dispat_commit
    "dispat-version"    = var.dispat_version
    "apt-snapshot"      = var.apt_snapshot
    "kernel-ref"        = var.kernel_ref
    "kernel-repo"       = var.kernel_repo
    "source-slots"      = tostring(var.source_slots)
    "crosstool-targets" = var.crosstool_targets
  }
  startup = file("${path.module}/../../scripts/kernel/node-startup.sh")
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

# The signing secret of the run (execution.secretEnv): only ever an
# environment variable of `dispat release` and `dispat worker`.
resource "random_id" "execution_secret" { byte_length = 32 }

module "orchestrator" {
  source          = "../modules/gce-node"
  name            = "${var.name_prefix}-par-c3"
  machine_type    = var.orchestrator_machine_type
  zone            = var.zone_a
  image           = var.image
  disk_gb         = var.disk_gb
  max_run_seconds = var.max_run_seconds
  subnetwork      = google_compute_subnetwork.subnet.id
  startup_script  = local.startup
  ssh_keys        = "${local.operator_line}\n${local.mailbox_line}"
  metadata        = merge(local.common_metadata, { "node-role" = "orchestrator" })
  labels          = { purpose = "dispat-kernel-parity", role = "orchestrator" }
}

module "worker" {
  source          = "../modules/gce-node"
  name            = "${var.name_prefix}-par-t2d"
  machine_type    = var.worker_machine_type
  zone            = var.zone_b
  image           = var.image
  disk_gb         = var.disk_gb
  max_run_seconds = var.max_run_seconds
  subnetwork      = google_compute_subnetwork.subnet.id
  startup_script  = local.startup
  ssh_keys        = local.operator_line
  metadata        = merge(local.common_metadata, { "node-role" = "worker" })
  labels          = { purpose = "dispat-kernel-parity", role = "worker" }
}

module "solo" {
  count           = var.solo ? 1 : 0
  source          = "../modules/gce-node"
  name            = "${var.name_prefix}-solo-c3"
  machine_type    = var.orchestrator_machine_type
  zone            = var.zone_b
  image           = var.image
  disk_gb         = var.disk_gb
  max_run_seconds = var.max_run_seconds
  subnetwork      = google_compute_subnetwork.subnet.id
  startup_script  = local.startup
  ssh_keys        = local.operator_line
  metadata        = merge(local.common_metadata, { "node-role" = "solo" })
  labels          = { purpose = "dispat-kernel-parity", role = "solo" }
}

# What run.sh reads. The secrets directory is ignored by git.
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
  value = merge({
    orchestrator = { name = module.orchestrator.name, zone = module.orchestrator.zone, internal_ip = module.orchestrator.internal_ip, external_ip = module.orchestrator.external_ip }
    worker       = { name = module.worker.name, zone = module.worker.zone, internal_ip = module.worker.internal_ip, external_ip = module.worker.external_ip }
  }, var.solo ? { solo = { name = module.solo[0].name, zone = module.solo[0].zone, internal_ip = module.solo[0].internal_ip, external_ip = module.solo[0].external_ip } } : {})
}
output "node_user" { value = local.node_user }
output "project" { value = var.project }
