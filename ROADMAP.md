# Roadmap

The project advances by evidence gates, not vague version labels.

## Gate A - Control Core

Status: **PASSED REAL_LOCAL**

Proven:

- PostgreSQL durability
- Temporal workflow execution
- OPA authorization
- retry/idempotency behavior
- `UNKNOWN` outcome preservation
- worker restart recovery

Authoritative evidence: `docs/operations/REAL_CONTROL_CORE_PROOF.md`.

## Gate B - Real Software Worker

Status: **NEXT**

Required proof:

- coding-agent benchmark
- real sandbox boundary
- real GitHub runtime adapter
- GitHub issue -> WorkItem -> patch -> tests -> PR
- adversarial containment
- independent verification before authorization

Candidate agent comparisons remain:

- mini-SWE-agent + SWE-ReX
- OpenHands headless / SDK

## Gate C - Supply Chain + Operability

Status: **PLANNED**

Required proof:

- Syft
- Trivy
- Grype
- immutable artifacts
- Cosign
- provenance
- OpenTelemetry
- `OperationalContract`
- topology
- change/runtime lineage

## Gate D - Real Operations

Status: **PLANNED**

Required proof:

- Alertmanager
- alert -> WorkItem
- real staging
- health evaluation
- rollback
- progressive delivery

## Gate E - Limited Autonomous Production

Status: **DISABLED / FUTURE**

Only after evidence permits:

- narrow LOW-risk `AUTO_PROD`
- deterministic canary promotion
- automatic rollback
- provider/dependency maintenance

HIGH and CRITICAL risk paths remain human-gated unless explicitly re-evaluated with evidence.
