# Autonomous Software Operations Control Plane

This repository is the working implementation of a self-hosted, open-source-first **Software Operations Control Plane**.

It is not merely an AI coding agent, DevOps bot, SRE assistant, CI/CD replacement, or incident chatbot. The product thesis is that **Software Operations is a first-class product plane**: the system that governs how software is understood, changed, verified, authorized, built, released, observed, recovered, and maintained.

Core invariant:

```text
LLMs propose.
Deterministic systems authorize.
Untrusted text never grants authority.
```

## What This Project Is

The control plane is designed to safely orchestrate:

- human requests
- GitHub issues
- production alerts
- external dependency and provider changes

into:

```text
investigation
-> scoped work
-> controlled agent execution
-> independent verification
-> authorization
-> release
-> observation
-> rollback/remediation
```

The durable value is the control loop: product-owned state, policy, evidence, audit, reproducible execution, independent verification, and human authority where policy requires it.

## Current Architecture

The target architecture is:

```text
Signal
-> WorkItem
-> RiskAssessment
-> PolicyDecision
-> Temporal
-> controlled execution
-> verification
-> GitHub
-> build/release
-> staging/canary
-> observation
```

The upstream control core is now proven locally with real PostgreSQL, Temporal, and OPA. Several downstream pieces remain fixture-level or design-only until later gates: real coding agent execution, real sandboxing, GitHub issue-to-PR automation, scanners, signing/provenance, telemetry, alert ingestion, staging, canary, rollback, and production autonomy.

## Current Verified State

**Gate A has PASSED at `REAL_LOCAL`.**

Proven live:

- PostgreSQL durability
- Temporal workflow execution
- Temporal worker restart recovery
- real OPA execution
- fail-closed policy behavior
- stable idempotency
- duplicate mutation suppression
- `UNKNOWN` outcome preservation

Not yet proven:

- real coding agent
- real sandbox
- GitHub issue -> autonomous PR
- real security scanners
- signing/provenance
- OpenTelemetry
- Alertmanager
- real staging
- real rollback
- real canary
- production autonomy

## Current Phase

**Gate B is next. It has not started in this repository state.**

Gate B target:

```text
REAL ISSUE
-> REAL WORKITEM
-> REAL OPA
-> REAL TEMPORAL
-> REAL SANDBOX
-> REAL CODING AGENT
-> REAL PATCH
-> REAL TESTS
-> REAL GITHUB PR
```

The SRE control-plane repository itself is a protected, high-risk target. The control plane is not currently allowed to autonomously modify its own authority, security, or control code. Self-hosting and self-remediation are future architecture problems, not current behavior.

## Readiness Vocabulary

Use these qualifiers whenever status could be ambiguous:

| Level | Meaning |
|---|---|
| `DESIGN_ONLY` | Described or planned, but not integrated in executable product flow. |
| `LOCAL_FIXTURE` | Exercised only through local fakes, fixtures, in-memory adapters, or developer-mode paths. |
| `REAL_LOCAL` | Executed against a real local runtime or binary with product code paths. |
| `REAL_NONPROD` | Executed against a real external/non-production service boundary. |
| `REAL_STAGING` | Executed against a staging environment with production-shaped controls. |
| `PRODUCTION_VERIFIED` | Proven in production with evidence, policy, observability, rollback, and ownership controls. |

## Current Readiness Matrix

| Capability | Current status |
|---|---|
| PostgreSQL | `REAL_LOCAL` |
| Temporal | `REAL_LOCAL` |
| OPA | `REAL_LOCAL` |
| GitHub repository publication | `REAL_NONPROD` |
| GitHub runtime adapter | `LOCAL_FIXTURE` / not real |
| Coding agent | not started |
| Sandbox | `LOCAL_FIXTURE` |
| Syft | `DESIGN_ONLY` |
| Trivy | `DESIGN_ONLY` |
| Grype | `DESIGN_ONLY` |
| Cosign | `DESIGN_ONLY` |
| OpenTelemetry | `DESIGN_ONLY` |
| Prometheus / Alertmanager | `DESIGN_ONLY` |
| Staging | `LOCAL_FIXTURE` |
| Canary | `LOCAL_FIXTURE` |
| Rollback | `LOCAL_FIXTURE` |
| Production autonomy | disabled |

## Security And Authority

Agent may:

- inspect authorized repository context
- propose changes
- write inside a sandbox
- produce structured evidence

Agent may not:

- mutate policy
- widen `ScopeGrant`
- alter its risk classification
- push directly to `main`
- deploy directly
- access production secrets
- authorize itself

Authority boundaries:

- OPA provides deterministic authorization.
- Temporal provides durable orchestration.
- PostgreSQL stores durable product/control state.
- Humans remain final authority where policy requires it.

## First-Class Software Operations Plane

The long-term product model is not:

```text
PRODUCT
+ external SRE bot
```

It is:

```text
PRODUCT SYSTEM
|-- BUSINESS / DOMAIN PLANE
`-- SOFTWARE OPERATIONS PLANE
```

The Software Operations Plane should eventually consume declared topology, operability contracts, health contracts, dependency metadata, release identity, runtime observations, and rollback/reconciliation rules. It must not infer all product semantics from logs.

Future managed systems should expose enough operational metadata for the control plane to understand:

- product topology
- component ownership
- operational contracts
- dependency graph
- change lineage
- release lineage
- runtime lineage
- health
- incidents
- rollback and reconciliation

## Documentation Status Hierarchy

Authoritative order:

1. [README.md](README.md): current product overview and current status.
2. [docs/architecture/INITIAL_ARCHITECTURE_REVIEW.md](docs/architecture/INITIAL_ARCHITECTURE_REVIEW.md): original architectural reasoning and historical baseline.
3. [docs/operations/REAL_CONTROL_CORE_PROOF.md](docs/operations/REAL_CONTROL_CORE_PROOF.md): authoritative Gate A evidence.
4. [docs/operations/STRETCH_PHASE_REPORT.md](docs/operations/STRETCH_PHASE_REPORT.md): current stretch roadmap/status.
5. [docs/operations/PHASE_1_HARDENING_REPORT.md](docs/operations/PHASE_1_HARDENING_REPORT.md): hardening history updated with latest state.
6. [docs/operations/INTEGRATION_EVIDENCE_MATRIX.md](docs/operations/INTEGRATION_EVIDENCE_MATRIX.md): current verification level per integration.
7. Future Gate B/C reports.

Older documents may preserve historical facts only when explicitly marked as historical or superseded.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the gate-based roadmap.

## Run Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
