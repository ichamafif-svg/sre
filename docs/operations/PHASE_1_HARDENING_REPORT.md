# Phase 1 Hardening Report

Date: 2026-10-04

Status: In progress. Phase 1 is not complete.

STATUS: SUPERSEDED FOR CURRENT READINESS BY `docs/operations/REAL_CONTROL_CORE_PROOF.md` AND `README.md`.

Stretch checkpoint update:

- Gate A live proof passed using local installed binaries.
- No transition to Gate B has been made yet.
- See `docs/operations/REAL_CONTROL_CORE_PROOF.md`.

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
| Temporal Server | Temporal CLI dev server `1.9.1`, server `1.32.0` | `REAL_LOCAL` proof passed |
| Temporal Python SDK | `temporalio==1.34.0` | `REAL_LOCAL` workflow/activity path proven |
| PostgreSQL | Postgres.app PostgreSQL `16.15` | `REAL_LOCAL` migration and persistence proven |
| OPA | `opa 1.7.1` | `REAL_LOCAL` policy execution and fail-closed behavior proven |

## Known Limitations

- Historical state at the first hardening checkpoint: the environment did not yet have local OPA, Temporal, or PostgreSQL binaries available to this repository.
- Current state: local binaries were installed under `.tools`, and Gate A passed at `REAL_LOCAL`; see `docs/operations/REAL_CONTROL_CORE_PROOF.md`.
- GitHub runtime adapter, real sandbox, real coding agent benchmark, scanners, signing, OpenTelemetry, Alertmanager, staging, canary, and rollback remain pending.
- `V2Workflow` still uses the developer-mode local policy by default for existing local tests; production Temporal path is now separated and ready for live proof.

## Readiness Labels

| Integration | Readiness |
|---|---|
| Temporal | `REAL_LOCAL` |
| PostgreSQL | `REAL_LOCAL` |
| OPA | `REAL_LOCAL` |
| Local V2 control behavior | `LOCAL_FIXTURE` |
| GitHub repository publication | `REAL_NONPROD` |

## Next Required Step

Historical next step at the earlier checkpoint was to run local Phase 1 infrastructure:

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

Current next step is Gate B: real issue to real WorkItem to real OPA/Temporal to real sandbox/coding agent to real tests and GitHub PR. No Gate B implementation has started in this document.
