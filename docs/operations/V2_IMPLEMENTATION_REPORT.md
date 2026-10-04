# V2 Implementation Report

Date: 2026-10-04

## Classification

Production-shaped local vertical slice. Not production-ready.

## Architecture Built

Implemented a modular monolith under `src/control_plane/` with:

- WorkItem lifecycle and strict state transitions.
- Structured risk model.
- Action-level policy decisions.
- Rego policy draft plus a deterministic local policy evaluator.
- Replaceable `AgentBackend` interface.
- Sandboxed execution result validation by changed path.
- Independent verification runner.
- In-memory GitHub-style PR/merge adapter.
- Immutable artifact builder with digest, local development signature, and provenance record.
- Deployment controller with staging, canary fractions, health evaluation, and rollback.
- Alert and human prompt ingestion.
- Fixture parser remediation scenario.

## Actual Dependency Versions

No third-party runtime dependencies are installed in this local scaffold. Python standard library only.

External dependencies are represented as ports/adapters for later integration:

- Temporal: not wired yet.
- PostgreSQL: not wired yet.
- OPA CLI/server: Rego draft exists; local evaluator mirrors initial policy.
- GitHub API: in-memory adapter only.
- Syft/Trivy/Grype/Cosign/SLSA: modeled in verification/build evidence only; real tool execution not wired yet.
- Argo CD/Argo Rollouts: not wired yet.
- OpenTelemetry/Prometheus/Alertmanager: telemetry and alert interfaces started; live integrations not wired yet.

## Licenses

Current code is original project code. Planned external integrations remain aligned with the license matrix in `docs/architecture/INITIAL_ARCHITECTURE_REVIEW.md`.

## Component Ownership

- `workitems`: lifecycle state machine.
- `signals`: signal normalization and incident classification.
- `risk`: deterministic risk assessment.
- `policy`: action authorization.
- `agents`: replaceable coding worker interface.
- `sandbox`: bounded execution and scope verification.
- `verification`: independent checks and evidence.
- `git`: PR/merge adapter.
- `builds`: artifact digest/signature/provenance.
- `deployment`: staging/canary/rollback controller.
- `health`: deterministic health criteria.
- `evidence`, `audit`, `telemetry`: storage and observability seams.

## Trust Boundaries

The LLM/agent backend can only produce a patch object. It cannot mutate WorkItem states, merge, deploy, or change policy. Scope is checked after execution from actual changed paths. Production promotion is human-gated by policy.

## Authority Boundaries

Implemented action permissions:

- `INVESTIGATE`
- `EXECUTE_SANDBOX`
- `OPEN_PR`
- `AUTO_MERGE`
- `DEPLOY_STAGING`
- `DEPLOY_CANARY`
- `DEPLOY_PRODUCTION`
- `ROLLBACK`
- `REQUIRE_HUMAN`
- `BLOCK`

Initial policy allows narrow LOW-risk auto-merge after verification, allows staging/canary, and requires human approval for production.

## Agent Backend Benchmark and Selection

The code includes an evaluation record for mini-SWE-agent + SWE-ReX, OpenHands headless/SDK, and the local fixture backend. The real benchmark has not been executed because neither external agent runtime is installed in this workspace.

Temporary selected backend: `FixtureParserAgent`, for deterministic V2 workflow validation only.

## Test Totals

Command:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Result:

- 5 tests passing.

## Adversarial Results

Covered:

- Prompt injection in human issue text cannot grant production deployment authority.
- Malicious agent patch attempting to modify policy is blocked by scope validation before PR creation.

## Chaos / Failure Results

Covered:

- Canary metric degradation stops promotion and rolls back to the previous known-good artifact.

Not yet covered:

- Worker restart.
- OPA unavailable.
- GitHub unavailable.
- Prometheus unavailable.
- Scanner timeout.
- Duplicate destructive action.
- Rollback failure path beyond no-previous-artifact handling.

## Security Findings

Current security posture is design-level:

- No production secrets are present.
- Agent has no merge/deploy authority.
- Sensitive paths are forbidden by scope.
- Production promotion is policy-human-gated.

Real scanner execution, SBOM artifacts, and Cosign signatures are not yet implemented.

## Staging Results

The fixture remediation deploys an immutable artifact digest to the local staging environment and evaluates deterministic health criteria.

## Canary Results

The fixture remediation supports 5%, 25%, 50%, and 100% canary phases with deterministic health gates.

## Rollback Evidence

The rollback test seeds a previous known-good artifact, deploys a candidate, observes degraded canary health, and restores the previous artifact.

## Cost Measurements

No model calls are made in this scaffold, so token/model cost is zero.

## Model Usage

No LLM model backend is executed. The fixture backend is deterministic.

## Known Limitations

- Temporal is not yet running the workflow.
- PostgreSQL is not yet the state store.
- OPA is not yet invoked as a live policy engine.
- GitHub API is not yet integrated.
- Real agent backend comparison is not yet executed.
- Real sandbox isolation is not yet enforced at OS/container level.
- Security scanners and SBOM generation are simulated.
- Artifact signing is a local development hash, not Cosign.
- Deployment is local in-memory, not Kubernetes/Argo or a real container target.
- OpenTelemetry/Prometheus/Alertmanager are not yet live.

## Production Readiness Classification

Not production-ready. Suitable for continuing implementation and validating control boundaries.

## Policy Actions Still Disabled

- Autonomous production deployment.
- High-risk auto-merge.
- Critical-risk execution.
- Production secret access by agents.
- Policy modification by agents.

## Deviations from Initial Architecture Review

- V1 PR-only stop was intentionally superseded by the V2 execution update.
- Implementation now models staging, canary, promotion gating, and rollback from the start.
- Local deterministic adapters were used before full OSS integrations to prove boundaries quickly.

## Recommended Next Autonomy Level

Proceed to Phase 1 hardening:

1. Wire Temporal for workflow durability.
2. Add PostgreSQL repositories.
3. Execute OPA policies with the OPA CLI/server in tests.
4. Replace fixture agent with the mini-SWE-agent/SWE-ReX versus OpenHands benchmark harness.
5. Add real OS/container sandboxing.
6. Add Syft/Trivy/Grype/Cosign integration behind the existing verification/build ports.

