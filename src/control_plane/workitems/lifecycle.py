from __future__ import annotations

from control_plane.domain import WorkItem, WorkItemState


ALLOWED_TRANSITIONS: dict[WorkItemState, set[WorkItemState]] = {
    WorkItemState.RECEIVED: {WorkItemState.NORMALIZED, WorkItemState.REJECTED},
    WorkItemState.NORMALIZED: {WorkItemState.TRIAGED, WorkItemState.REJECTED},
    WorkItemState.TRIAGED: {WorkItemState.SCOPED, WorkItemState.ESCALATED},
    WorkItemState.SCOPED: {WorkItemState.AUTHORIZED_FOR_INVESTIGATION, WorkItemState.BLOCKED},
    WorkItemState.AUTHORIZED_FOR_INVESTIGATION: {WorkItemState.INVESTIGATING},
    WorkItemState.INVESTIGATING: {WorkItemState.INVESTIGATION_COMPLETE, WorkItemState.FAILED},
    WorkItemState.INVESTIGATION_COMPLETE: {WorkItemState.PLANNED, WorkItemState.CLOSED, WorkItemState.ESCALATED},
    WorkItemState.PLANNED: {WorkItemState.AUTHORIZED_FOR_EXECUTION, WorkItemState.BLOCKED},
    WorkItemState.AUTHORIZED_FOR_EXECUTION: {WorkItemState.EXECUTING},
    WorkItemState.EXECUTING: {WorkItemState.VERIFYING, WorkItemState.BLOCKED, WorkItemState.FAILED},
    WorkItemState.VERIFYING: {WorkItemState.VERIFIED, WorkItemState.BLOCKED, WorkItemState.FAILED},
    WorkItemState.VERIFIED: {WorkItemState.PR_READY, WorkItemState.BLOCKED},
    WorkItemState.PR_READY: {WorkItemState.AWAITING_MERGE_AUTHORIZATION},
    WorkItemState.AWAITING_MERGE_AUTHORIZATION: {WorkItemState.MERGED, WorkItemState.ESCALATED, WorkItemState.REJECTED},
    WorkItemState.MERGED: {WorkItemState.BUILDING},
    WorkItemState.BUILDING: {WorkItemState.BUILD_VERIFIED, WorkItemState.FAILED},
    WorkItemState.BUILD_VERIFIED: {WorkItemState.STAGING, WorkItemState.BLOCKED},
    WorkItemState.STAGING: {WorkItemState.STAGING_OBSERVING, WorkItemState.FAILED},
    WorkItemState.STAGING_OBSERVING: {WorkItemState.CANARY, WorkItemState.ROLLING_BACK, WorkItemState.ESCALATED},
    WorkItemState.CANARY: {WorkItemState.CANARY_OBSERVING, WorkItemState.FAILED},
    WorkItemState.CANARY_OBSERVING: {WorkItemState.CANARY, WorkItemState.PRODUCTION, WorkItemState.ROLLING_BACK, WorkItemState.ESCALATED},
    WorkItemState.PRODUCTION: {WorkItemState.PRODUCTION_OBSERVING, WorkItemState.ROLLING_BACK},
    WorkItemState.PRODUCTION_OBSERVING: {WorkItemState.CLOSED, WorkItemState.ROLLING_BACK, WorkItemState.ESCALATED},
    WorkItemState.ROLLING_BACK: {WorkItemState.ROLLED_BACK, WorkItemState.FAILED},
    WorkItemState.ROLLED_BACK: {WorkItemState.ESCALATED, WorkItemState.CLOSED},
    WorkItemState.BLOCKED: {WorkItemState.ESCALATED, WorkItemState.REJECTED},
    WorkItemState.FAILED: {WorkItemState.ESCALATED, WorkItemState.CLOSED},
    WorkItemState.ESCALATED: {WorkItemState.CLOSED, WorkItemState.REJECTED},
    WorkItemState.REJECTED: set(),
    WorkItemState.CLOSED: set(),
}


def transition(item: WorkItem, target: WorkItemState, reason: str) -> None:
    allowed = ALLOWED_TRANSITIONS[item.state]
    if target not in allowed:
        raise ValueError(f"illegal transition {item.state.value} -> {target.value}")
    item.record(f"{item.state.value}->{target.value}: {reason}")
    item.state = target
