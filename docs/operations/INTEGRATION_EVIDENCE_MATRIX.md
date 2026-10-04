# Integration Evidence Matrix

Date: 2026-10-04

| Component | Version | License | Integration status | Verification level | Test evidence | Known limitations |
|---|---:|---|---|---|---|---|
| Temporal Server | Temporal CLI dev server `1.9.1`, server `1.32.0` | MIT | Persistent local dev server via `.tools/temporal-dev.db` | REAL_LOCAL | Worker killed/restarted; workflow resumed to `AUTHORIZED_FOR_INVESTIGATION` | Dev server, not production cluster |
| Temporal Python SDK | `temporalio==1.34.0` | MIT | Workflow and activities added | REAL_LOCAL | Live workflow completed after worker restart | Multi-arg activity SDK issue fixed with `args=[...]` |
| PostgreSQL | Postgres.app PostgreSQL `16.15` | PostgreSQL License | Local server, migrations, repository | REAL_LOCAL | Migration applied; state persisted after server restart | Local Postgres.app binary, not managed production DB |
| OPA | `opa 1.7.1` | Apache-2.0 | Rego decision schema, CLI adapter, local server | REAL_LOCAL | `opa check`, server evaluation, fail-closed tests | OPA server auth not configured for production |
| GitHub | Existing connector/SSH | GitHub service | Local push completed previously | REAL_NONPROD | Repo `ichamafif-svg/sre` populated | Runtime GitHub adapter still in-memory |
| Sandbox | Existing logical runner | N/A | Still simulated | LOCAL_FIXTURE | Existing adversarial tests | Real process/container isolation pending |
| Security scanners | Syft/Trivy/Grype planned | Apache-2.0 | Not integrated | DESIGN_ONLY | None | Pending Phase 1 later step |
| Cosign | Planned | Apache-2.0 | Not integrated | DESIGN_ONLY | None | Pending Phase 1 later step |
| OpenTelemetry | Planned | Apache-2.0 | Not integrated | DESIGN_ONLY | None | Pending Phase 1 later step |
| Prometheus/Alertmanager | Planned | Apache-2.0 | Not integrated | DESIGN_ONLY | None | Pending Phase 1 later step |
| Staging/canary target | Planned Docker target | N/A | Still in-memory | LOCAL_FIXTURE | Existing e2e tests | Real deployment boundary pending |
