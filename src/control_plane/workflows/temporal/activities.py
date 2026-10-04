from __future__ import annotations

import os
from dataclasses import asdict

from control_plane.domain import Signal, SignalKind, WorkItemState
from control_plane.idempotency import stable_idempotency_key
from control_plane.persistence.postgres import PostgresStore
from control_plane.signals.ingest import normalize
from control_plane.workitems.lifecycle import transition

try:  # pragma: no cover - import is exercised when phase1 deps are installed
    from temporalio import activity
except ImportError:  # pragma: no cover
    activity = None


def _store() -> PostgresStore:
    dsn = os.environ["CONTROL_PLANE_DATABASE_URL"]
    return PostgresStore(dsn)


if activity:

    @activity.defn
    async def normalize_signal_activity(signal_payload: dict) -> dict:
        signal = Signal(
            id=signal_payload["id"],
            kind=SignalKind(signal_payload["kind"]),
            summary=signal_payload["summary"],
            payload=signal_payload.get("payload", {}),
            source=signal_payload["source"],
        )
        item = normalize(signal)
        store = _store()
        store.upsert_work_item(item)
        store.add_audit_event(
            item.id,
            "normalized signal",
            stable_idempotency_key(item.id, "normalize-signal"),
        )
        return {
            "work_item_id": item.id,
            "state": item.state.value,
            "signal_id": signal.id,
            "summary": item.summary,
        }

    @activity.defn
    async def advance_state_activity(work_item_snapshot: dict, target_state: str, reason: str) -> dict:
        # Phase 1 proof activity: domain transition is still validated by the
        # WorkItem state machine, while Temporal owns retry/timers/history.
        signal = Signal(
            id=work_item_snapshot["signal_id"],
            kind=SignalKind(work_item_snapshot.get("signal_kind", SignalKind.HUMAN_PROMPT.value)),
            summary=work_item_snapshot["summary"],
            payload={},
            source=work_item_snapshot.get("signal_source", "temporal"),
        )
        item = normalize(signal)
        item.id = work_item_snapshot["work_item_id"]
        item.state = WorkItemState(work_item_snapshot["state"])
        transition(item, WorkItemState(target_state), reason)
        store = _store()
        store.upsert_work_item(item)
        store.add_audit_event(
            item.id,
            reason,
            stable_idempotency_key(item.id, target_state, reason),
        )
        return {
            "work_item_id": item.id,
            "state": item.state.value,
            "signal_id": signal.id,
            "summary": item.summary,
        }

