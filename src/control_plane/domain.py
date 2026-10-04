from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class WorkItemState(str, Enum):
    RECEIVED = "RECEIVED"
    NORMALIZED = "NORMALIZED"
    TRIAGED = "TRIAGED"
    SCOPED = "SCOPED"
    AUTHORIZED_FOR_INVESTIGATION = "AUTHORIZED_FOR_INVESTIGATION"
    INVESTIGATING = "INVESTIGATING"
    INVESTIGATION_COMPLETE = "INVESTIGATION_COMPLETE"
    PLANNED = "PLANNED"
    AUTHORIZED_FOR_EXECUTION = "AUTHORIZED_FOR_EXECUTION"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    VERIFIED = "VERIFIED"
    BLOCKED = "BLOCKED"
    PR_READY = "PR_READY"
    AWAITING_MERGE_AUTHORIZATION = "AWAITING_MERGE_AUTHORIZATION"
    MERGED = "MERGED"
    BUILDING = "BUILDING"
    BUILD_VERIFIED = "BUILD_VERIFIED"
    STAGING = "STAGING"
    STAGING_OBSERVING = "STAGING_OBSERVING"
    CANARY = "CANARY"
    CANARY_OBSERVING = "CANARY_OBSERVING"
    PRODUCTION = "PRODUCTION"
    PRODUCTION_OBSERVING = "PRODUCTION_OBSERVING"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"
    CLOSED = "CLOSED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


class PolicyAction(str, Enum):
    INVESTIGATE = "INVESTIGATE"
    EXECUTE_SANDBOX = "EXECUTE_SANDBOX"
    OPEN_PR = "OPEN_PR"
    AUTO_MERGE = "AUTO_MERGE"
    DEPLOY_STAGING = "DEPLOY_STAGING"
    DEPLOY_CANARY = "DEPLOY_CANARY"
    DEPLOY_PRODUCTION = "DEPLOY_PRODUCTION"
    ROLLBACK = "ROLLBACK"
    REQUIRE_HUMAN = "REQUIRE_HUMAN"
    BLOCK = "BLOCK"


class Permission(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    HUMAN = "HUMAN"


class RiskClass(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SignalKind(str, Enum):
    HUMAN_PROMPT = "HUMAN_PROMPT"
    GITHUB_ISSUE = "GITHUB_ISSUE"
    ALERT = "ALERT"
    FAILED_DEPLOYMENT = "FAILED_DEPLOYMENT"
    HEALTH_DEGRADATION = "HEALTH_DEGRADATION"
    EXTERNAL_MAINTENANCE = "EXTERNAL_MAINTENANCE"


class IncidentClass(str, Enum):
    OUR_CODE = "OUR_CODE"
    EXTERNAL_PROVIDER = "EXTERNAL_PROVIDER"
    CONFIGURATION = "CONFIGURATION"
    CREDENTIAL = "CREDENTIAL"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    SECURITY = "SECURITY"
    EXPECTED_FAILURE = "EXPECTED_FAILURE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Signal:
    kind: SignalKind
    summary: str
    payload: dict[str, Any]
    source: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class ScopeGrant:
    allowed_paths: tuple[str, ...]
    forbidden_paths: tuple[str, ...]
    allowed_tools: tuple[str, ...]
    forbidden_tools: tuple[str, ...]
    allowed_environments: tuple[str, ...]
    maximum_blast_radius: str


@dataclass(frozen=True)
class RiskAssessment:
    risk_class: RiskClass
    change_type: str
    blast_radius: str
    reversibility: str
    data_sensitivity: str
    security_sensitivity: str
    infrastructure_sensitivity: str
    database_impact: str
    policy_authorization_impact: str
    verification_strength: str
    reproduction_strength: str
    architecture_impact: str
    affected_tenants_users: str
    confidence: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class PolicyDecision:
    permissions: dict[PolicyAction, Permission]
    required_human_actions: tuple[PolicyAction, ...]
    blocked_reasons: tuple[str, ...]
    policy_version: str = "local-v2-0"

    def permission_for(self, action: PolicyAction) -> Permission:
        if self.permissions.get(PolicyAction.BLOCK) == Permission.ALLOW:
            return Permission.DENY
        return self.permissions.get(action, Permission.DENY)

    def assert_allowed(self, action: PolicyAction) -> None:
        permission = self.permission_for(action)
        if permission != Permission.ALLOW:
            raise PermissionError(f"{action.value} is {permission.value}")


@dataclass
class WorkItem:
    signal: Signal
    summary: str
    state: WorkItemState = WorkItemState.RECEIVED
    id: str = field(default_factory=lambda: str(uuid4()))
    incident_class: IncidentClass = IncidentClass.UNKNOWN
    scope: ScopeGrant | None = None
    risk: RiskAssessment | None = None
    policy_decision: PolicyDecision | None = None
    evidence: list[str] = field(default_factory=list)
    audit: list[str] = field(default_factory=list)
    release_id: str | None = None
    pr_id: str | None = None

    def record(self, event: str) -> None:
        self.audit.append(event)

