# One experiment node: a Compute Engine VM with a bounded lifetime that deletes
# itself when it expires, provisioned by a startup script that reads the rest
# of its instructions from instance metadata. The shapes and images are the
# ones the parity runs of 2026-09-22 used; they are inputs, not defaults.
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0"
    }
  }
}

variable "name" { type = string }
variable "machine_type" { type = string }
variable "zone" { type = string }
variable "image" {
  type        = string
  description = "Exact image name, for example ubuntu-2404-noble-amd64-v20260918 (project ubuntu-os-cloud)."
}
variable "image_project" {
  type    = string
  default = "ubuntu-os-cloud"
}
variable "disk_gb" { type = number }
variable "max_run_seconds" {
  type        = number
  description = "The VM deletes itself after this many seconds, whatever state the experiment is in."
}
variable "subnetwork" { type = string }
variable "startup_script" { type = string }
variable "metadata" {
  type    = map(string)
  default = {}
}
variable "ssh_keys" {
  type        = string
  description = "Lines of `user:public-key` for the guest agent (metadata ssh-keys)."
}
variable "labels" {
  type    = map(string)
  default = {}
}

resource "google_compute_instance" "node" {
  name         = var.name
  machine_type = var.machine_type
  zone         = var.zone
  labels       = var.labels

  boot_disk {
    initialize_params {
      image = "projects/${var.image_project}/global/images/${var.image}"
      size  = var.disk_gb
      type  = "pd-balanced"
    }
  }

  network_interface {
    subnetwork = var.subnetwork
    access_config {} # an ephemeral external address: apt, kernel.org, GitHub
  }

  scheduling {
    provisioning_model          = "STANDARD"
    instance_termination_action = "DELETE"
    max_run_duration {
      seconds = var.max_run_seconds
    }
  }

  metadata = merge(var.metadata, {
    "startup-script" = var.startup_script
    "ssh-keys"       = var.ssh_keys
    "enable-oslogin" = "FALSE"
  })

  # Nothing here calls a Google API from inside the VM.
  service_account {
    scopes = ["logging-write", "monitoring-write"]
  }
}

output "name" { value = google_compute_instance.node.name }
output "zone" { value = google_compute_instance.node.zone }
output "internal_ip" { value = google_compute_instance.node.network_interface[0].network_ip }
output "external_ip" { value = google_compute_instance.node.network_interface[0].access_config[0].nat_ip }
