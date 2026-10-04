from __future__ import annotations

from datetime import timedelta

try:  # pragma: no cover - imported when phase1 deps are installed
    from temporalio import workflow
    from temporalio.common import RetryPolicy
except ImportError:  # pragma: no cover
    workflow = None
    RetryPolicy = None

if workflow:
    with workflow.unsafe.imports_passed_through():
        from control_plane.domain import WorkItemState
        from control_plane.workflows.temporal.activities import advance_state_activity, normalize_signal_activity

    ACTIVITY_RETRY_POLICY = RetryPolicy(
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(seconds=30),
        maximum_attempts=5,
    )

    @workflow.defn
    class WorkItemTemporalWorkflow:
        @workflow.run
        async def run(self, signal_payload: dict) -> dict:
            workflow.logger.info("starting WorkItem workflow")
            snapshot = await workflow.execute_activity(
                normalize_signal_activity,
                signal_payload,
                start_to_close_timeout=timedelta(seconds=20),
                retry_policy=ACTIVITY_RETRY_POLICY,
            )
            for state, reason in (
                (WorkItemState.TRIAGED.value, "temporal phase1 triage proof"),
                (WorkItemState.SCOPED.value, "temporal phase1 scope proof"),
                (WorkItemState.AUTHORIZED_FOR_INVESTIGATION.value, "temporal phase1 investigation authorization proof"),
            ):
                snapshot = await workflow.execute_activity(
                    advance_state_activity,
                    snapshot,
                    state,
                    reason,
                    start_to_close_timeout=timedelta(seconds=20),
                    retry_policy=ACTIVITY_RETRY_POLICY,
                )
            return snapshot

