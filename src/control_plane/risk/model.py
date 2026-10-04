from __future__ import annotations

from control_plane.domain import RiskAssessment, RiskClass, Signal, SignalKind


HIGH_MARKERS = ("auth", "permission", "secret", "billing", "schema", "migration", "policy", "deploy")
CRITICAL_MARKERS = ("root credential", "destructive production", "privilege escalation", "data loss")


def assess_risk(signal: Signal, changed_paths: tuple[str, ...] = ()) -> RiskAssessment:
    text = f"{signal.summary} {' '.join(changed_paths)}".lower()
    payload_text = " ".join(str(value).lower() for value in signal.payload.values())
    reasons: list[str] = []
    risk = RiskClass.LOW

    if any(marker in text for marker in CRITICAL_MARKERS):
        risk = RiskClass.CRITICAL
        reasons.append("critical marker present")
    elif any(marker in text for marker in HIGH_MARKERS):
        risk = RiskClass.HIGH
        reasons.append("high-sensitivity marker present")
    elif signal.kind in {SignalKind.ALERT, SignalKind.FAILED_DEPLOYMENT, SignalKind.HEALTH_DEGRADATION} and (
        "fixture-parser" in payload_text or "parser regression" in payload_text
    ):
        risk = RiskClass.LOW
        reasons.append("bounded fixture parser incident with known rollback")
    elif signal.kind in {SignalKind.ALERT, SignalKind.FAILED_DEPLOYMENT, SignalKind.HEALTH_DEGRADATION}:
        risk = RiskClass.MEDIUM
        reasons.append("production-style signal")
    else:
        reasons.append("narrow non-sensitive change")

    if any(path.startswith(("policy/", "deploy/production", "src/control_plane/policy")) for path in changed_paths):
        risk = max(risk, RiskClass.HIGH, key=lambda item: ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(item.value))
        reasons.append("sensitive path changed")

    return RiskAssessment(
        risk_class=risk,
        change_type="bugfix" if signal.kind in {SignalKind.ALERT, SignalKind.HEALTH_DEGRADATION} else "request",
        blast_radius="fixture-service" if risk in {RiskClass.LOW, RiskClass.MEDIUM} else "shared-control-plane",
        reversibility="artifact rollback available",
        data_sensitivity="none",
        security_sensitivity="none" if risk in {RiskClass.LOW, RiskClass.MEDIUM} else "sensitive",
        infrastructure_sensitivity="none",
        database_impact="none",
        policy_authorization_impact="none",
        verification_strength="pending",
        reproduction_strength="pending",
        architecture_impact="none",
        affected_tenants_users="test fixture users",
        confidence="deterministic-facts",
        reasons=tuple(reasons),
    )
