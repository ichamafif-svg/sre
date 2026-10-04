from __future__ import annotations

import os
from pathlib import Path

from control_plane.domain import ScopeGrant, Signal, SignalKind, WorkItemState
from control_plane.idempotency import stable_idempotency_key
from control_plane.persistence.postgres import PostgresStore
from control_plane.policy.opa import OpaPolicyEngine
from control_plane.risk.model import assess_risk
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
            "signal_kind": signal.kind.value,
            "signal_source": signal.source,
            "summary": item.summary,
        }

    @activity.defn
    async def evaluate_policy_activity(work_item_snapshot: dict) -> dict:
        signal = Signal(
            id=work_item_snapshot["signal_id"],
            kind=SignalKind(work_item_snapshot["signal_kind"]),
            summary=work_item_snapshot["summary"],
            payload={},
            source=work_item_snapshot["signal_source"],
        )
        risk = assess_risk(signal)
        scope = ScopeGrant(
            allowed_paths=("service/parser.py", "tests"),
            forbidden_paths=("policy/", "deploy/production", "src/control_plane/policy"),
            allowed_tools=("python-test", "security-scan", "sbom"),
            forbidden_tools=("git-merge", "deploy-production", "secret-read"),
            allowed_environments=("sandbox", "ci", "staging", "canary"),
            maximum_blast_radius="fixture-service",
        )
        opa_binary = os.environ.get("OPA_BINARY", ".tools/bin/opa")
        policy_path = Path(os.environ.get("OPA_POLICY_PATH", "policy/rego/autonomy.rego"))
        decision = OpaPolicyEngine(policy_path=policy_path, opa_binary=opa_binary).decide(
            risk,
            scope,
            verification_passed=True,
            changed_paths=("service/parser.py",),
            security_status="PASS",
        )
        store = _store()
        # Persist a minimal WorkItem row before attaching decision evidence.
        item = normalize(signal)
        item.id = work_item_snapshot["work_item_id"]
        item.state = WorkItemState(work_item_snapshot["state"])
        item.risk = risk
        store.upsert_work_item(item)
        store.add_policy_decision(item.id, decision)
        store.add_audit_event(
            item.id,
            f"policy evaluated {decision.policy_version}",
            stable_idempotency_key(item.id, "evaluate-policy", decision.policy_version),
        )
        return {
            **work_item_snapshot,
            "policy_version": decision.policy_version,
            "policy_blocked_reasons": list(decision.blocked_reasons),
        }

    @activity.defn
    async def reserve_external_mutation_activity(work_item_snapshot: dict, operation: str) -> dict:
        store = _store()
        key = stable_idempotency_key(work_item_snapshot["work_item_id"], operation)
        record = store.reserve_external_mutation(work_item_snapshot["work_item_id"], operation, key)
        store.add_audit_event(
            work_item_snapshot["work_item_id"],
            f"external mutation reserved {operation}",
            stable_idempotency_key(work_item_snapshot["work_item_id"], "audit", "reserve", operation),
        )
        return {
            **work_item_snapshot,
            "external_mutation_key": record.idempotency_key,
            "external_mutation_status": record.status,
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
            "signal_kind": signal.kind.value,
            "signal_source": signal.source,
            "summary": item.summary,
        }
