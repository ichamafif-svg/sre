package autonomy

default allow := false

risk := input.risk.risk_class
verification_passed := input.verification_passed

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
  action == "EXECUTE_SANDBOX"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk != "CRITICAL"
  action == "OPEN_PR"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk == "LOW"
  verification_passed
  action == "AUTO_MERGE"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk != "CRITICAL"
  action == "DEPLOY_STAGING"
  decision := "ALLOW"
}

permission[action] := decision if {
  risk != "CRITICAL"
  action == "DEPLOY_CANARY"
  decision := "ALLOW"
}

permission[action] := decision if {
  action == "DEPLOY_PRODUCTION"
  decision := "HUMAN"
}
