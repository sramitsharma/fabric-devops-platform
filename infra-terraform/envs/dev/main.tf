locals {
  registry = yamldecode(file("${path.module}/../../../tenant-registry/tenants.yaml"))
  tenants  = { for t in local.registry.tenants : t.id => t if contains(t.envs, var.env) }
}

module "eventhub_tenant" {
  source   = "../../modules/eventhub-tenant"
  for_each = local.tenants

  tenant_id        = each.key
  tier             = each.value.tier          # premium => dedicated namespace
  hubs             = each.value.eventhubs
  throughput_units = each.value.throughput_units
  env              = var.env
  tags = {
    tenant              = each.key
    env                 = var.env
    data-classification = "confidential"
    cost-centre         = "dp-${each.key}"
  }
}

module "fabric_gold_workspace" {
  source   = "../../modules/fabric-workspace"   # microsoft/fabric provider
  for_each = local.tenants
  name     = "gold-${each.key}-${var.env}"
  capacity = var.fabric_capacity_id
  tags     = { tenant = each.key, env = var.env }
}
