# Phase 1 Hardening Report

Date: 2026-10-04

Status: In progress. Phase 1 is not complete.

## Scope Completed In This Pass

Started the de-simulation phase without changing the V2 domain model:

- Added PostgreSQL migration and repository for product-owned state.
- Added external mutation idempotency records.
- Added OPA Rego decision output and real OPA CLI adapter.
- Added Temporal workflow/activity integration modules.
- Added explicit Temporal retry policy instead of relying on unbounded default activity retries.
- Added local Phase 1 Docker Compose for PostgreSQL, Temporal, Temporal UI, and OPA.
- Added evidence matrix.

## Temporal Defaults Verification

Current source/doc checks performed on 2026-10-04:

- Temporal Python SDK `RetryPolicy` defaults: initial interval 1s, backoff coefficient 2.0, maximum interval defaults to 100x initial interval, maximum attempts 0 means unlimited.
- Temporal docs state default Activity retry policy retries indefinitely with exponential backoff and recommend setting `MaximumAttempts` for fixed-count retry scenarios.
- Activity execution must set either Start-To-Close or Schedule-To-Close timeout.

Implementation decision:

- `WorkItemTemporalWorkflow` uses explicit `RetryPolicy(maximum_attempts=5, initial_interval=1s, maximum_interval=30s)` and `start_to_close_timeout=20s` for proof activities.
- Mutating activities use stable idempotency keys derived from WorkItem/action identity, not retry attempt or process restart count.

Sources:

- https://github.com/temporalio/sdk-python/blob/main/temporalio/common.py
- https://github.com/temporalio/documentation/blob/main/docs/design-patterns/fixed-count-retries.mdx
- https://github.com/temporalio/documentation/blob/main/docs/develop/typescript/activities/timeouts.mdx

## Retry / Idempotency Matrix

| Operation | Retry owner | Retryable failures | Non-retryable failures | Unknown outcome handling | Idempotency key source | Reconciliation |
|---|---|---|---|---|---|---|
| Normalize signal to WorkItem | Temporal Activity | transient DB connection, worker restart | malformed signal schema | Treat as unknown; check `audit_events` and `work_items` by ID | `sha256(work_item_id, normalize-signal)` | Read WorkItem row and audit key |
| Advance WorkItem state | Temporal Activity | transient DB connection, worker restart | illegal domain transition | Treat as unknown; check audit key | `sha256(work_item_id, target_state, reason)` | Read WorkItem state and audit key |
| External mutation reservation | PostgreSQL transaction | transient DB connection | duplicate incompatible operation | Existing reservation is authoritative | caller-provided logical operation key | Read `external_mutations` |

## Real Components Added

| Component | Version | Status |
|---|---:|---|
| Temporal Server | `temporalio/auto-setup:1.29.7` | Compose only, not yet proven live |
| Temporal Python SDK | `temporalio==1.34.0` | Code integration added |
| PostgreSQL | `postgres:16.4` | Migration and repository added |
| OPA | `openpolicyagent/opa:1.7.1-debug` | Rego and CLI adapter added |

## Known Limitations

- Current execution environment does not have `docker` or `opa` installed, so live compose and OPA CLI smoke tests were not run in this pass.
- Temporal worker restart proof has not been executed yet.
- PostgreSQL restart persistence proof has not been executed yet.
- OPA binary was not available in the current test path, so fail-closed behavior is coded but not integration-tested here.
- GitHub runtime adapter, real sandbox, real coding agent benchmark, scanners, signing, OpenTelemetry, Alertmanager, staging, canary, and rollback remain pending.
- `V2Workflow` still uses the developer-mode local policy by default for existing local tests; production Temporal path is now separated and ready for live proof.

## Readiness Labels

| Integration | Readiness |
|---|---|
| Temporal | DESIGN_ONLY, pending REAL_LOCAL proof |
| PostgreSQL | DESIGN_ONLY, pending REAL_LOCAL proof |
| OPA | DESIGN_ONLY, pending REAL_LOCAL proof |
| Local V2 control behavior | LOCAL_FIXTURE |
| GitHub repository publication | REAL_NONPROD |

## Next Required Step

Run local Phase 1 infrastructure:

```bash
docker compose -f deploy/phase1/docker-compose.yml up -d
python -m pip install -e '.[phase1]'
CONTROL_PLANE_DATABASE_URL=postgresql://control_plane:control_plane@localhost:5432/control_plane python scripts/migrate_postgres.py
CONTROL_PLANE_DATABASE_URL=postgresql://control_plane:control_plane@localhost:5432/control_plane python scripts/run_temporal_worker.py
```

In another shell:

```bash
CONTROL_PLANE_DATABASE_URL=postgresql://control_plane:control_plane@localhost:5432/control_plane python scripts/start_temporal_workflow.py
```

Then kill/restart `scripts/run_temporal_worker.py` during a longer workflow proof and verify no duplicate audit or external mutation rows.
