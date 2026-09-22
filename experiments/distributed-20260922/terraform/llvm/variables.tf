variable "project" {
  type        = string
  description = "The Google Cloud project; the measured pair used the project named dispat."
}
variable "region" {
  type    = string
  default = "us-central1"
}
variable "zone" {
  type    = string
  default = "us-central1-a"
}
variable "name_prefix" {
  type    = string
  default = "dispat-llvm"
}
variable "image" {
  type        = string
  default     = "ubuntu-2404-noble-amd64-v20260918"
  description = "The image the family ubuntu-2404-lts-amd64 resolved to on 2026-09-22 (Ubuntu 24.04.5)."
}
variable "orchestrator_machine_type" {
  type    = string
  default = "e2-standard-4"
}
variable "worker_machine_type" {
  type        = string
  default     = "n2-custom-14-49152"
  description = "7 cores, 14 threads, 48 GiB: the workers of the pair, and the single node of its baseline."
}
variable "orchestrator_disk_gb" {
  type    = number
  default = 80
}
variable "worker_disk_gb" {
  type    = number
  default = 150
}
variable "max_run_seconds" {
  type        = number
  default     = 28800
  description = "Eight hours, as the measured set; the pair itself takes about ninety minutes plus setup."
}
variable "subnet_cidr" {
  type    = string
  default = "10.20.0.0/24"
}
variable "ssh_source_ranges" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}
variable "dispat_commit" {
  type        = string
  default     = "272772cb62a874289e97c5efbfab1a5c33b03efc"
  description = "The commit the matrix pair's binary was built from (a clean rebuild is sha256 46bc2cf8…)."
}
variable "dispat_version" {
  type    = string
  default = "1.11.0-rc.4+main.272772cb"
}
variable "apt_snapshot" {
  type    = string
  default = "20260922T000000Z"
}
