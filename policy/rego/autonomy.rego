package autonomy

actions := [
  "INVESTIGATE",
  "EXECUTE_SANDBOX",
  "OPEN_PR",
  "AUTO_MERGE",
  "DEPLOY_STAGING",
  "DEPLOY_CANARY",
  "DEPLOY_PRODUCTION",
  "ROLLBACK",
  "REQUIRE_HUMAN",
  "BLOCK",
]

risk := input.risk.risk_class
verification_passed := input.verification_passed
changed_paths := input.changed_paths
forbidden_paths := input.scope.forbidden_paths
security_status := input.security.status

forbidden_path_hit if {
  some path in changed_paths
  some prefix in forbidden_paths
  startswith(path, prefix)
}

security_block if {
  security_status == "CRITICAL_FINDING"
}

security_block if {
  security_status == "SCANNER_FAILED"
}

permission[action] := decision if {
  action == "INVESTIGATE"
  decision := "ALLOW"
}

permission[action] := decision if {
  action == "ROLLBACK"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk != "CRITICAL"
  not forbidden_path_hit
  action == "EXECUTE_SANDBOX"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk != "CRITICAL"
  not forbidden_path_hit
  not security_block
  action == "OPEN_PR"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk == "LOW"
  verification_passed
  not forbidden_path_hit
  not security_block
  action == "AUTO_MERGE"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk != "CRITICAL"
  not forbidden_path_hit
  not security_block
  action == "DEPLOY_STAGING"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk != "CRITICAL"
  not forbidden_path_hit
  not security_block
  action == "DEPLOY_CANARY"
  decision := "ALLOW"
}

permission[action] := decision if {
  action == "DEPLOY_PRODUCTION"
  decision := "HUMAN"
}

permission[action] := decision if {
  action == "REQUIRE_HUMAN"
  decision := "ALLOW"
}

permission[action] := decision if {
  action == "BLOCK"
  risk == "CRITICAL"
  decision := "ALLOW"
}

permission[action] := decision if {
  action == "BLOCK"
  forbidden_path_hit
  decision := "ALLOW"
}

permission[action] := decision if {
  action == "BLOCK"
  security_block
  decision := "ALLOW"
}

blocked_reasons contains "critical risk blocks autonomous execution" if {
  risk == "CRITICAL"
}

blocked_reasons contains "changed path intersects forbidden scope" if {
  forbidden_path_hit
}

blocked_reasons contains "security gate blocks privileged action" if {
  security_block
}

required_human_actions contains "DEPLOY_PRODUCTION"

required_human_actions contains "AUTO_MERGE" if {
  risk != "LOW"
}

defaulted_permissions[action] := "DENY" if {
  some action in actions
  not permission[action]
}

merged_permissions[action] := decision if {
  decision := permission[action]
}

merged_permissions[action] := decision if {
  decision := defaulted_permissions[action]
}

decision := {
  "policy_version": "rego-v2-phase1-0",
  "permissions": merged_permissions,
  "required_human_actions": required_human_actions,
  "blocked_reasons": blocked_reasons,
}
