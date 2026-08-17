package main

# Deny any storage/eventhub resource with public network access
deny[msg] {
  r := input.resource_changes[_]
  r.change.after.public_network_access_enabled == true
  msg := sprintf("public network access enabled on %s", [r.address])
}

# Mandatory tags — cost, tenancy, and classification are non-negotiable
required_tags := {"tenant", "env", "cost-centre", "data-classification"}
deny[msg] {
  r := input.resource_changes[_]
  r.change.after.tags
  missing := required_tags - {k | r.change.after.tags[k]}
  count(missing) > 0
  msg := sprintf("%s missing tags: %v", [r.address, missing])
}

# No secrets in plan values
deny[msg] {
  r := input.resource_changes[_]
  walk(r.change.after, [_, v])
  is_string(v)
  regex.match(`(?i)(password|accountkey|sharedaccesskey)=`, v)
  msg := sprintf("possible inline secret on %s", [r.address])
}
