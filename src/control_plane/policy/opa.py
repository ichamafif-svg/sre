from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.domain import Permission, PolicyAction, PolicyDecision, RiskAssessment, ScopeGrant


class OpaUnavailable(RuntimeError):
    pass


class MalformedOpaDecision(RuntimeError):
    pass


@dataclass(frozen=True)
class OpaPolicyEngine:
    policy_path: Path = Path("policy/rego/autonomy.rego")
    package_query: str = "data.autonomy.decision"
    opa_binary: str = "opa"

    def decide(
        self,
        risk: RiskAssessment,
        scope: ScopeGrant,
        *,
        verification_passed: bool = False,
        changed_paths: tuple[str, ...] = (),
        security_status: str = "PASS",
    ) -> PolicyDecision:
        trusted_input = {
            "risk": {"risk_class": risk.risk_class.value},
            "scope": {
                "allowed_paths": list(scope.allowed_paths),
                "forbidden_paths": list(scope.forbidden_paths),
                "allowed_tools": list(scope.allowed_tools),
                "forbidden_tools": list(scope.forbidden_tools),
                "allowed_environments": list(scope.allowed_environments),
                "maximum_blast_radius": scope.maximum_blast_radius,
            },
            "verification_passed": verification_passed,
            "changed_paths": list(changed_paths),
            "security": {"status": security_status},
        }
        try:
            completed = subprocess.run(
                [
                    self.opa_binary,
                    "eval",
                    "--format",
                    "json",
                    "--data",
                    str(self.policy_path),
                    "--stdin-input",
                    self.package_query,
                ],
                input=json.dumps(trusted_input),
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            raise OpaUnavailable("OPA unavailable; privileged action must fail closed") from exc

        if completed.returncode != 0:
            raise OpaUnavailable(completed.stderr.strip() or "OPA returned non-zero exit")

        try:
            payload = json.loads(completed.stdout)
            decision = payload["result"][0]["expressions"][0]["value"]
            return self._parse_decision(decision)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as exc:
            raise MalformedOpaDecision("OPA decision schema is malformed") from exc

    @staticmethod
    def _parse_decision(raw: dict[str, Any]) -> PolicyDecision:
        permissions_raw = raw.get("permissions")
        if not isinstance(permissions_raw, dict):
            raise MalformedOpaDecision("missing permissions")
        permissions = {
            PolicyAction(action): Permission(permission)
            for action, permission in permissions_raw.items()
        }
        required = tuple(PolicyAction(action) for action in raw.get("required_human_actions", []))
        blocked = tuple(str(reason) for reason in raw.get("blocked_reasons", []))
        version = str(raw.get("policy_version", "unknown"))
        for action in PolicyAction:
            permissions.setdefault(action, Permission.DENY)
        return PolicyDecision(permissions, required, blocked, version)


def fail_closed_decision(reason: str) -> PolicyDecision:
    permissions = {action: Permission.DENY for action in PolicyAction}
    permissions[PolicyAction.BLOCK] = Permission.ALLOW
    permissions[PolicyAction.REQUIRE_HUMAN] = Permission.ALLOW
    return PolicyDecision(
        permissions=permissions,
        required_human_actions=(PolicyAction.REQUIRE_HUMAN,),
        blocked_reasons=(reason,),
        policy_version="fail-closed",
    )
