variable "tenant" {}
variable "environment" {}
variable "capacity_id" {}

resource "fabric_workspace" "gold" {
  display_name = "ws-${var.tenant}-gold-${var.environment}"
  capacity_id  = var.capacity_id
  description  = "Gold workspace for tenant ${var.tenant} (${var.environment}) — managed by Terraform"
}

resource "fabric_workspace_role_assignment" "tenant_readers" {
  workspace_id = fabric_workspace.gold.id
  principal = {
    id   = var.tenant_reader_group_id
    type = "Group"
  }
  role = "Viewer"
}
variable "tenant_reader_group_id" { default = null }

output "workspace_id" { value = fabric_workspace.gold.id }
