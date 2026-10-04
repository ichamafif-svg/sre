# Real Control Core Proof

Date: 2026-10-04

Status: **GATE A CORE PROOF PASSED FOR LOCAL BINARIES**

## Required Gate A Proof

Gate A requires live proof that PostgreSQL, Temporal, and OPA are operating as real integrations:

1. Start PostgreSQL, Temporal, and OPA.
2. Apply migrations.
3. Start a real Temporal worker.
4. Create a real WorkItem.
5. Persist it in PostgreSQL.
6. Evaluate authorization through real OPA.
7. Execute workflow transitions through Temporal.
8. Record audit events.
9. Reserve an external mutation with stable idempotency.
10. Kill and restart the worker during workflow execution.
11. Prove workflow resume.
12. Prove no duplicate external mutation or non-idempotent audit effect.
13. Prove coherent WorkItem state.

## Current Environment Observation

The current host initially lacked system-level tools, but the missing runtime was installed locally under the repository:

- Python virtualenv: `.venv`
- OPA CLI: `.tools/bin/opa`, version `1.7.1`
- Temporal CLI/dev server: `.tools/bin/temporal`, version `1.9.1`, server `1.32.0`
- PostgreSQL: `.tools/Postgres.app/Contents/Versions/16/bin/postgres`, version `16.15`
- PostgreSQL client: `.tools/Postgres.app/Contents/Versions/16/bin/psql`, version `16.15`

Bundled Python is available:

- `/Users/ichamafif/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`
- Version observed: `Python 3.12.14`

## Live Proof Evidence

PostgreSQL:

- Initialized a local data directory at `.tools/pgdata`.
- Started PostgreSQL on `localhost:5432`.
- Created database `control_plane`.
- Applied `migrations/postgres/001_control_plane.sql` through the real `psycopg` repository path.
- Stopped PostgreSQL deliberately and observed an explicit `OperationalError`.
- Restarted PostgreSQL and verified WorkItem and external mutation state persisted.

Temporal:

- Started Temporal dev server with persistent workflow store:
  - `.tools/bin/temporal server start-dev --ip 127.0.0.1 --port 7233 --ui-port 8233 --db-filename .tools/temporal-dev.db`
- First run revealed an SDK integration error in multi-argument activity invocation.
- Fixed the workflow to use `args=[...]`.
- Started a fresh workflow against persistent Temporal.
- Killed the Temporal worker during the workflow delay.
- Restarted the worker.
- The same workflow resumed and completed to `AUTHORIZED_FOR_INVESTIGATION`.

OPA:

- Real OPA policy compile initially failed due unsafe Rego variables.
- Fixed the Rego implementation without changing policy semantics.
- `opa check policy/rego` passed.
- OPA server started on `localhost:8181`.
- Live server evaluation returned `rego-v2-phase1-0` with `DEPLOY_PRODUCTION: HUMAN`.
- OPA unavailable and malformed policy response paths both returned fail-closed decisions in application code.

Idempotency:

- Workflow reserved an external mutation using stable key `bd31d0f96e033780d5eacee22032944a6928b942cefa5a404deb62a2ce315bdd`.
- Repeating the same logical reservation produced one row, not duplicates.
- Audit for the recovered WorkItem had six events and six distinct audit idempotency keys.

UNKNOWN outcome:

- Recorded `gate-a-unknown-outcome-proof` with status `UNKNOWN`.
- Verified it remained `UNKNOWN`, not `FAILED`.

## Final Evidence Snapshot

Latest recovered WorkItem:

- `work_item_id`: `da1148d1-c954-4b6b-8a43-d7c4504babcf`
- `signal_id`: `221ae1a9-1d3b-4c57-963e-d16b3005b941`
- `state`: `AUTHORIZED_FOR_INVESTIGATION`
- `version`: `4`

External mutation:

- `operation`: `gate-a-proof-mutation`
- `status`: `RESERVED`
- `key_count`: `1`

Audit:

- `audit_count`: `6`
- `distinct_audit_keys`: `6`

## Architecture Freeze Assessment

Current port:

- PostgreSQL product-state repository.
- Temporal workflow and activity modules.
- OPA policy adapter.

Real provider/tool behavior:

- Temporal Python SDK required multi-argument activities to be invoked with `args=[...]`.
- OPA v1 rejected unsafe partial object rule heads that were accepted by no local test double.
- PostgreSQL required unsandboxed shared memory access.

Mismatches fixed:

- Temporal activity invocation updated to `args=[...]`.
- Rego policy rewritten to valid OPA v1 syntax.
- Gate A proof uses local binaries instead of Docker because Docker is not available.

## Probe Command

```bash
/Users/ichamafif/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/gate_a_control_core_probe.py
```

Expected current result after local installs:

- `READY_TO_RUN`

## Gate A Invariants

Proven for local worker/service failure:

- `PROCESS FAILURE != STATE LOSS`
- `RETRY != DUPLICATE SIDE EFFECT`
- `OPA FAILURE = DENY / BLOCK`
- `UNKNOWN != FAILED`

Remaining caveat:

- Temporal is proven using the CLI development server with persistent SQLite, not a production Temporal cluster.
Gate B may proceed only as `REAL_LOCAL` / `REAL_NONPROD`, not production-verified.
