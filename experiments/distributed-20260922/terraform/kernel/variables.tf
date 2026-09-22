variable "project" {
  type        = string
  description = "The Google Cloud project; the measured runs used dispat-linux-parity."
}
variable "region" {
  type    = string
  default = "us-central1"
}
variable "zone_a" {
  type        = string
  default     = "us-central1-a"
  description = "Zone of the orchestrator (par-c3 ran here)."
}
variable "zone_b" {
  type        = string
  default     = "us-central1-b"
  description = "Zone of the worker and the solo node (t2d-standard-8 was unavailable in us-central1-a on 2026-09-22; the quota is regional)."
}
variable "name_prefix" {
  type    = string
  default = "dispat-kernel"
}
variable "image" {
  type        = string
  default     = "ubuntu-2404-noble-amd64-v20260918"
  description = "The image the family ubuntu-2404-lts-amd64 resolved to on 2026-09-22 (Ubuntu 24.04.5)."
}
variable "orchestrator_machine_type" {
  type    = string
  default = "c3-standard-22"
}
variable "worker_machine_type" {
  type    = string
  default = "t2d-standard-8"
}
variable "disk_gb" {
  type    = number
  default = 100
}
variable "max_run_seconds" {
  type        = number
  default     = 7200
  description = "The nodes delete themselves after this; the measured pair lived 22 minutes."
}
variable "solo" {
  type        = bool
  default     = false
  description = "Also create the single node of the same-hardware pair."
}
variable "subnet_cidr" {
  type    = string
  default = "10.10.0.0/24"
}
variable "ssh_source_ranges" {
  type        = list(string)
  default     = ["0.0.0.0/0"]
  description = "Where run.sh connects from; narrow it to your address."
}
variable "dispat_commit" {
  type        = string
  default     = "f0c9e9594fc87dda325aa323a1a82de53bd23cca"
  description = "The commit the round-2 binary was built from (sha256 63441cc6…, unstamped)."
}
variable "dispat_version" {
  type        = string
  default     = ""
  description = "The -X cli.Version stamp; empty reproduces the unstamped round-2 binary."
}
variable "apt_snapshot" {
  type    = string
  default = "20260922T000000Z"
}
variable "kernel_ref" {
  type    = string
  default = "v7.3-rc4"
}
variable "kernel_repo" {
  type    = string
  default = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git"
}
variable "source_slots" {
  type        = number
  default     = 5
  description = "Pristine source trees per node; m68k_nommu builds five cells at once on the orchestrator."
}
variable "crosstool_targets" {
  type    = string
  default = "alpha-linux m68k-linux"
}
