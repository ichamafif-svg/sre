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

permission["INVESTIGATE"] := decision if {
  decision := "ALLOW"
}

permission["ROLLBACK"] := decision if {
  decision := "ALLOW"
}

permission["EXECUTE_SANDBOX"] := decision if {
  risk != "CRITICAL"
  not forbidden_path_hit
  decision := "ALLOW"
}

permission["OPEN_PR"] := decision if {
  risk != "CRITICAL"
  not forbidden_path_hit
  not security_block
  decision := "ALLOW"
}

permission["AUTO_MERGE"] := decision if {
  risk == "LOW"
  verification_passed
  not forbidden_path_hit
  not security_block
  decision := "ALLOW"
}

permission["DEPLOY_STAGING"] := decision if {
  risk != "CRITICAL"
  not forbidden_path_hit
  not security_block
  decision := "ALLOW"
}

permission["DEPLOY_CANARY"] := decision if {
  risk != "CRITICAL"
  not forbidden_path_hit
  not security_block
  decision := "ALLOW"
}

permission["DEPLOY_PRODUCTION"] := decision if {
  decision := "HUMAN"
}

permission["REQUIRE_HUMAN"] := decision if {
  decision := "ALLOW"
}

permission["BLOCK"] := decision if {
  risk == "CRITICAL"
  decision := "ALLOW"
}

permission["BLOCK"] := decision if {
  forbidden_path_hit
  decision := "ALLOW"
}

permission["BLOCK"] := decision if {
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
