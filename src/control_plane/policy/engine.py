from __future__ import annotations

from control_plane.domain import Permission, PolicyAction, PolicyDecision, RiskAssessment, RiskClass, ScopeGrant


class LocalPolicyEngine:
    """Deterministic policy evaluator mirroring policy/rego/autonomy.rego for local tests."""

    def decide(self, risk: RiskAssessment, scope: ScopeGrant, *, verification_passed: bool = False) -> PolicyDecision:
        permissions = {action: Permission.DENY for action in PolicyAction}
        blocked: list[str] = []
        human: list[PolicyAction] = []

        permissions[PolicyAction.INVESTIGATE] = Permission.ALLOW
        permissions[PolicyAction.ROLLBACK] = Permission.ALLOW

        if risk.risk_class == RiskClass.CRITICAL:
            permissions[PolicyAction.BLOCK] = Permission.ALLOW
            blocked.append("critical risk blocks autonomous execution")
            return PolicyDecision(permissions, tuple(human), tuple(blocked))

        permissions[PolicyAction.EXECUTE_SANDBOX] = Permission.ALLOW
        permissions[PolicyAction.OPEN_PR] = Permission.ALLOW
        permissions[PolicyAction.DEPLOY_STAGING] = Permission.ALLOW
        permissions[PolicyAction.DEPLOY_CANARY] = Permission.ALLOW

        if risk.risk_class == RiskClass.LOW and verification_passed:
            permissions[PolicyAction.AUTO_MERGE] = Permission.ALLOW
        elif risk.risk_class == RiskClass.LOW:
            permissions[PolicyAction.AUTO_MERGE] = Permission.DENY
            blocked.append("auto-merge requires completed verification")
        else:
            permissions[PolicyAction.AUTO_MERGE] = Permission.HUMAN
            human.append(PolicyAction.AUTO_MERGE)

        permissions[PolicyAction.DEPLOY_PRODUCTION] = Permission.HUMAN
        permissions[PolicyAction.REQUIRE_HUMAN] = Permission.ALLOW
        human.append(PolicyAction.DEPLOY_PRODUCTION)

        if not scope.allowed_paths:
            permissions[PolicyAction.BLOCK] = Permission.ALLOW
            blocked.append("empty scope")

        return PolicyDecision(permissions, tuple(human), tuple(blocked))

