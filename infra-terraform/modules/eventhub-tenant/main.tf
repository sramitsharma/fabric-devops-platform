# Hub-per-tenant isolation; premium tier gets a dedicated namespace.
resource "azurerm_eventhub_namespace" "dedicated" {
  count                         = var.tier == "premium" ? 1 : 0
  name                          = "ehns-${var.tenant_id}-${var.env}"
  sku                           = "Premium"
  capacity                      = var.throughput_units
  public_network_access_enabled = false          # OPA also enforces this
  minimum_tls_version           = "1.2"
  local_authentication_enabled  = false          # Entra ID only — no SAS keys
  resource_group_name           = var.rg
  location                      = var.location
  tags                          = var.tags
}

resource "azurerm_eventhub" "hub" {
  for_each          = toset(var.hubs)
  name              = "${var.tenant_id}-${each.value}"
  namespace_id      = var.tier == "premium" ? azurerm_eventhub_namespace.dedicated[0].id : var.shared_namespace_id
  partition_count   = 8
  message_retention = 3                          # replay window = RPO cover
}

# Per-tenant, least-privilege data-plane RBAC (no namespace-wide grants)
resource "azurerm_role_assignment" "producer" {
  for_each             = toset(var.hubs)
  scope                = azurerm_eventhub.hub[each.value].id
  role_definition_name = "Azure Event Hubs Data Sender"
  principal_id         = var.producer_principal_id
}

resource "azurerm_role_assignment" "replicator" {
  for_each             = toset(var.hubs)
  scope                = azurerm_eventhub.hub[each.value].id
  role_definition_name = "Azure Event Hubs Data Receiver"
  principal_id         = var.replicator_workload_identity_id
}
