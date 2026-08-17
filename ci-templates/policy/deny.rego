package main

deny[msg] {
  r := input.resource_changes[_]
  r.type == "azurerm_eventhub_namespace"
  r.change.after.public_network_access_enabled == true
  msg := sprintf("EH namespace %s must not allow public access", [r.address])
}

deny[msg] {
  r := input.resource_changes[_]
  r.change.after.tags
  not r.change.after.tags.tenant
  msg := sprintf("%s missing mandatory 'tenant' tag", [r.address])
}

deny[msg] {
  r := input.resource_changes[_]
  r.type == "azurerm_storage_account"
  r.change.after.min_tls_version != "TLS1_2"
  msg := sprintf("%s must enforce TLS1_2", [r.address])
}
