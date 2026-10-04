from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.domain import PolicyAction, PolicyDecision, Permission, WorkItem


class ConcurrencyConflict(RuntimeError):
    pass


@dataclass(frozen=True)
class MutationRecord:
    idempotency_key: str
    work_item_id: str
    operation: str
    status: str
    external_ref: str | None
    outcome: dict[str, Any]


class PostgresStore:
    """PostgreSQL-backed product state.

    Temporal owns workflow history. This repository owns product state and
    external mutation idempotency records.
    """

    def __init__(self, dsn: str):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:  # pragma: no cover - exercised in integration env
            raise RuntimeError("Install phase1 dependencies: pip install -e '.[phase1]'") from exc

        self._psycopg = psycopg
        self._dict_row = dict_row
        self.dsn = dsn

    def connect(self):
        return self._psycopg.connect(self.dsn, row_factory=self._dict_row)

    def migrate(self, migration_path: Path = Path("migrations/postgres/001_control_plane.sql")) -> None:
        sql = migration_path.read_text()
        with self.connect() as conn:
            conn.execute(sql)

    def upsert_work_item(self, item: WorkItem) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO work_items (
                  id, signal_id, signal_kind, signal_source, summary, state,
                  incident_class, risk_class, pr_id, release_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                  summary = EXCLUDED.summary,
                  state = EXCLUDED.state,
                  incident_class = EXCLUDED.incident_class,
                  risk_class = EXCLUDED.risk_class,
                  pr_id = EXCLUDED.pr_id,
                  release_id = EXCLUDED.release_id,
                  version = work_items.version + 1,
                  updated_at = now()
                """,
                (
                    item.id,
                    item.signal.id,
                    item.signal.kind.value,
                    item.signal.source,
                    item.summary,
                    item.state.value,
                    item.incident_class.value,
                    item.risk.risk_class.value if item.risk else None,
                    item.pr_id,
                    item.release_id,
                ),
            )

    def add_audit_event(self, work_item_id: str, event: str, idempotency_key: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_events (work_item_id, event, idempotency_key)
                VALUES (%s, %s, %s)
                ON CONFLICT (work_item_id, idempotency_key) DO NOTHING
                """,
                (work_item_id, event, idempotency_key),
            )

    def add_policy_decision(self, work_item_id: str, decision: PolicyDecision) -> None:
        permissions = {action.value: permission.value for action, permission in decision.permissions.items()}
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO policy_decisions (
                  work_item_id, policy_version, permissions,
                  required_human_actions, blocked_reasons
                )
                VALUES (%s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
                """,
                (
                    work_item_id,
                    decision.policy_version,
                    json.dumps(permissions),
                    json.dumps([action.value for action in decision.required_human_actions]),
                    json.dumps(list(decision.blocked_reasons)),
                ),
            )

    def reserve_external_mutation(self, work_item_id: str, operation: str, idempotency_key: str) -> MutationRecord:
        with self.connect() as conn:
            row = conn.execute(
                """
                INSERT INTO external_mutations (idempotency_key, work_item_id, operation, status)
                VALUES (%s, %s, %s, 'RESERVED')
                ON CONFLICT (idempotency_key) DO UPDATE SET idempotency_key = external_mutations.idempotency_key
                RETURNING idempotency_key, work_item_id, operation, status, external_ref, outcome
                """,
                (idempotency_key, work_item_id, operation),
            ).fetchone()
        return MutationRecord(
            idempotency_key=row["idempotency_key"],
            work_item_id=row["work_item_id"],
            operation=row["operation"],
            status=row["status"],
            external_ref=row["external_ref"],
            outcome=row["outcome"],
        )

    def complete_external_mutation(
        self,
        idempotency_key: str,
        *,
        status: str,
        external_ref: str | None,
        outcome: dict[str, Any],
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE external_mutations
                SET status = %s, external_ref = %s, outcome = %s::jsonb, updated_at = now()
                WHERE idempotency_key = %s
                """,
                (status, external_ref, json.dumps(outcome), idempotency_key),
            )


def policy_decision_from_row(row: dict[str, Any]) -> PolicyDecision:
    permissions = {
        PolicyAction(action): Permission(permission)
        for action, permission in row["permissions"].items()
    }
    return PolicyDecision(
        permissions=permissions,
        required_human_actions=tuple(PolicyAction(action) for action in row["required_human_actions"]),
        blocked_reasons=tuple(row["blocked_reasons"]),
        policy_version=row["policy_version"],
    )
