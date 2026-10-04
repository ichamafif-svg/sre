# Integration Evidence Matrix

Date: 2026-10-04

| Component | Version | License | Integration status | Verification level | Test evidence | Known limitations |
|---|---:|---|---|---|---|---|
| Temporal Server | `temporalio/auto-setup:1.29.7` | MIT | Adapter and local compose added | DESIGN_ONLY -> pending REAL_LOCAL run | Not yet run in this environment | Worker restart proof still pending |
| Temporal Python SDK | `temporalio==1.34.0` | MIT | Workflow and activities added | DESIGN_ONLY -> pending REAL_LOCAL run | Import gated until dependency install | Not yet proven against live service |
| PostgreSQL | `postgres:16.4` | PostgreSQL License | Schema and repository added | DESIGN_ONLY -> pending REAL_LOCAL run | Migration file present | Restart persistence test pending |
| OPA | `openpolicyagent/opa:1.7.1-debug` | Apache-2.0 | Rego decision schema and CLI adapter added | DESIGN_ONLY -> pending REAL_LOCAL run | Fail-closed adapter code present | OPA binary not executed in current tests |
| GitHub | Existing connector/SSH | GitHub service | Local push completed previously | REAL_NONPROD | Repo `ichamafif-svg/sre` populated | Runtime GitHub adapter still in-memory |
| Sandbox | Existing logical runner | N/A | Still simulated | LOCAL_FIXTURE | Existing adversarial tests | Real process/container isolation pending |
| Security scanners | Syft/Trivy/Grype planned | Apache-2.0 | Not integrated | DESIGN_ONLY | None | Pending Phase 1 later step |
| Cosign | Planned | Apache-2.0 | Not integrated | DESIGN_ONLY | None | Pending Phase 1 later step |
| OpenTelemetry | Planned | Apache-2.0 | Not integrated | DESIGN_ONLY | None | Pending Phase 1 later step |
| Prometheus/Alertmanager | Planned | Apache-2.0 | Not integrated | DESIGN_ONLY | None | Pending Phase 1 later step |
| Staging/canary target | Planned Docker target | N/A | Still in-memory | LOCAL_FIXTURE | Existing e2e tests | Real deployment boundary pending |

