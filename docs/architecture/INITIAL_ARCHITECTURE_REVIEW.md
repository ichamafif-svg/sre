# Initial Architecture Review: Autonomous SRE / Software Operations Control Plane

Date: 2026-10-04

Status: Draft for approval before implementation

## A. Problem Definition

This platform is a self-hosted, open-source-first software operations control plane. Its purpose is to turn operational signals, human requests, and external changes into controlled software work: investigation, evidence gathering, sandboxed code modification, deterministic verification, approval, and eventually safe staged rollout.

It is not an AI coding assistant, an unrestricted production agent, a replacement for CI/CD, a custom workflow engine, a custom policy language, a custom observability backend, or a dashboard-first product. The core product principle is:

> LLMs propose. Deterministic systems authorize.

The durable value is not a particular model or agent implementation. The durable value is the control loop, evidence, policy, audit trail, reproducible work environments, trusted build pipeline, and human decision model.

The long-term loop is:

`SIGNAL -> UNDERSTAND -> INVESTIGATE -> PLAN -> EXECUTE -> VERIFY -> AUTHORIZE -> DEPLOY -> OBSERVE -> LEARN`

V1 stops before autonomous production deployment.

## B. Existing Industry Building Blocks

Research notes are current as of 2026-10-04. Final adoption still requires a deeper proof-of-concept and legal review.

### Coding and Software Agents

| Capability | Candidate projects | License | Maturity / adoption signals | Pros | Limitations |
|---|---:|---|---|---|---|
| General software-development agent | OpenHands | MIT | Active public project; local Docker mode; cloud offering; published benchmark claims and paper; large contributor base | Broad agent platform, browser/API/tool use, GitHub issue flows | Large surface area; must be sandboxed and stripped of authority; cloud features should not become a dependency |
| SWE-bench style issue resolution | SWE-agent | MIT | Research-origin project; spawned SWE-ReX runtime; benchmark-oriented | Good fit for issue-to-patch experiments; strong emphasis on agent-computer interface | More research/eval oriented than full operations platform |
| Minimal coding agent | mini-SWE-agent | MIT | Packaged on PyPI; intentionally small | Useful as inspectable baseline; easier to reason about and constrain | Not a full product workflow; likely needs wrapping |
| Sandboxed execution interface | SWE-ReX | MIT | Built to power SWE-agent; supports Docker and cloud backends | Valuable as a sandbox adapter candidate | It is an execution framework, not an authorization boundary by itself |
| CLI pair programmer | Aider | Apache-2.0 | Large GitHub adoption; supports many model backends; Git integration | Mature local coding workflow; useful as a worker backend | Designed for interactive pair programming, not autonomous ops control |

Sources: OpenHands GitHub/license and benchmark notes, SWE-ReX GitHub, Aider GitHub/Homebrew, SWE-agent papers and docs.

### Durable Orchestration

| Capability | Candidate projects | License | Maturity / adoption signals | Pros | Limitations |
|---|---:|---|---|---|---|
| Durable application workflows | Temporal | MIT | Active releases; production customer claims; long lineage from Cadence/Uber/AWS SWF ideas | Excellent fit for long-running WorkItem workflows, retries, durable state, human wait states | Operational complexity; deterministic workflow constraints; needs careful SDK/version discipline |
| Kubernetes-native workflows | Argo Workflows | Apache-2.0 | Part of CNCF graduated Argo project | Fits cluster-native batch/workflow runs | More Kubernetes-centric; less application-stateful than Temporal |
| Event-driven Kubernetes automation | Argo Events | Apache-2.0 | Part of CNCF graduated Argo project | Useful later for signal ingestion in Kubernetes environments | Not a general WorkItem brain |

Recommendation: integrate Temporal for control-plane workflows; optionally use Argo Workflows later for cluster-native execution jobs.

### Policy and Authorization

| Capability | Candidate projects | License | Maturity / adoption signals | Pros | Limitations |
|---|---:|---|---|---|---|
| Policy engine | Open Policy Agent / Rego | Apache-2.0 | CNCF graduated; broadly used | General-purpose, testable, embeddable policy; clear separation from LLM | Rego policy quality is on us; decision context must be curated |
| Admission/policy for Kubernetes | Gatekeeper or Kyverno | Apache-2.0 | Common Kubernetes policy engines | Useful for deployment guardrails | V1 does not need cluster admission control |

Recommendation: integrate OPA for authorization decisions. Do not let LLMs produce authoritative policy inputs without deterministic validation.

### Observability

| Capability | Candidate projects | License | Maturity / adoption signals | Pros | Limitations |
|---|---:|---|---|---|---|
| Telemetry standard | OpenTelemetry | Apache-2.0 | CNCF graduated in 2026; very broad contributor base | Vendor-neutral traces, metrics, logs; avoids backend lock-in | Standards do not provide storage/query UX alone |
| Metrics and alerting | Prometheus + Alertmanager | Apache-2.0 | CNCF graduated; common production default | Reliable metrics/alerts; strong ecosystem | Long-term storage may require separate backend |
| Logs/traces backend | Grafana Loki / Tempo | AGPL-3.0 | Popular, mature | Good operational UX with Grafana stack | AGPL must be flagged; legal/product implications if modified or network-offered |
| Alternative observability backends | ClickHouse-based or OpenSearch-based stacks | Apache-2.0 varies | Mature ecosystems | Potentially more permissive depending on choice | Needs separate evaluation; operational overhead |

Recommendation: use OpenTelemetry as instrumentation standard and Prometheus/Alertmanager for V1 metrics/alerts. Defer final log/trace storage backend selection.

### Deployment and Progressive Delivery

| Capability | Candidate projects | License | Maturity / adoption signals | Pros | Limitations |
|---|---:|---|---|---|---|
| GitOps deployment | Argo CD | Apache-2.0 | CNCF graduated Argo subproject | Mature GitOps reconciler; separates Git truth from cluster state | Kubernetes-centric; V1 can defer deployment |
| Canary/blue-green rollout | Argo Rollouts | Apache-2.0 | CNCF graduated Argo subproject | Canary analysis, progressive delivery | Requires production observability and Kubernetes integration |
| Feature flag standard | OpenFeature | Apache-2.0 | CNCF incubating | Vendor-neutral feature-flag API | Does not itself provide full flag management |
| Self-hosted flag daemon | flagd | Apache-2.0 | OpenFeature ecosystem | Lightweight flag service | Needs operational hardening for prod |

Recommendation: design for Argo CD + Argo Rollouts later; do not implement deployment automation in V1. Use OpenFeature/flagd only when feature-control use cases exist.

### Security, SBOM, Signing, Provenance

| Capability | Candidate projects | License | Maturity / adoption signals | Pros | Limitations |
|---|---:|---|---|---|---|
| Vulnerability, secret, IaC, config scanning | Trivy | Apache-2.0 | Widely used scanner | Broad scanner coverage | Scanner results are assumptions, not truth; pin actions/binaries |
| SBOM generation | Syft | Apache-2.0 | Active Anchore project | Strong SBOM generation support | SBOM quality varies by ecosystem |
| Vulnerability scanning from SBOM/images | Grype | Apache-2.0 | Active Anchore project | Complements Syft; useful cross-check | Differences with Trivy must be reconciled |
| Artifact signing | Sigstore / Cosign | Apache-2.0 | OpenSSF/Sigstore ecosystem | Keyless signing, identity-bound signatures | Needs strict verifier policy and OIDC trust model |
| Supply-chain framework | SLSA | Community Specification License 1.0 for spec | Common supply-chain vocabulary | Good target model for provenance maturity | Spec is not implementation |

Recommendation: integrate these in CI as deterministic gates. V1 should generate SBOM and scan, but can initially require human review for ambiguous vulnerability findings.

### Infrastructure and Secrets

| Capability | Candidate projects | License | Maturity / adoption signals | Pros | Limitations |
|---|---:|---|---|---|---|
| Infrastructure as code | OpenTofu | MPL-2.0 | Linux Foundation hosted Terraform fork; active releases | Genuine OSS path after Terraform BUSL; compatible ecosystem | MPL obligations; provider ecosystem still needs license review |
| Secrets management | OpenBao | MPL-2.0 | OpenSSF sandbox project; Vault community fork | Self-hosted secret manager with open governance | Younger than Vault; operational maturity must be validated |
| Workload identity | SPIFFE/SPIRE | Apache-2.0 | CNCF graduated SPIFFE/SPIRE ecosystem | Good model for short-lived identities | Adds infra complexity; likely post-V1 |

Recommendation: prefer OpenTofu and OpenBao for later self-hosted infrastructure/secrets, but V1 can avoid needing production secrets.

### LLM Observability and Evaluation

| Capability | Candidate projects | License | Maturity / adoption signals | Pros | Limitations |
|---|---:|---|---|---|---|
| LLM traces/evals | Langfuse | MIT core; enterprise features gated | Self-hostable; core OSS; active project | Good first choice for agent run tracing/evals | Enterprise features and telemetry settings need review |
| AI observability/evals | Arize Phoenix | Elastic License 2.0 | Active project with broad usage | Strong LLM eval/observability capabilities | ELv2 is source-available, not OSI open source; flag for policy |

Recommendation: prefer Langfuse OSS or build directly on OpenTelemetry for V1 agent-run traces. Phoenix is useful to study but should be flagged due to license.

## License Matrix

| Project | Purpose | License status | Initial decision |
|---|---|---|---|
| Temporal | Durable workflows | MIT | INTEGRATE |
| OPA | Policy decisions | Apache-2.0 | INTEGRATE |
| OpenTelemetry | Telemetry standard | Apache-2.0 | INTEGRATE |
| Prometheus / Alertmanager | Metrics and alerts | Apache-2.0 | INTEGRATE |
| Argo CD / Rollouts / Workflows / Events | GitOps, rollout, workflows | Apache-2.0 | DEFER / INTEGRATE later |
| OpenFeature / flagd | Feature flag standard and daemon | Apache-2.0 | DEFER |
| Trivy | Security scanning | Apache-2.0 | INTEGRATE |
| Syft / Grype | SBOM and vulnerability scanning | Apache-2.0 | INTEGRATE |
| Sigstore / Cosign | Artifact signing | Apache-2.0 | INTEGRATE later; design now |
| SLSA | Supply-chain provenance model | Community Specification License 1.0 | EXTEND target model |
| OpenTofu | IaC | MPL-2.0 | DEFER / INTEGRATE later |
| OpenBao | Secrets | MPL-2.0 | DEFER / INTEGRATE later |
| OpenHands | Coding agent | MIT | WRAP candidate |
| SWE-agent / mini-SWE-agent / SWE-ReX | Coding agent and sandbox runtime | MIT | WRAP candidate |
| Aider | Coding agent CLI | Apache-2.0 | WRAP candidate |
| Langfuse | LLM observability | MIT core, EE features | WRAP or DEFER |
| Phoenix | LLM observability/evals | Elastic License 2.0 | REJECT for OSS-first dependency; study only |
| Grafana Loki / Tempo / Grafana | Logs/traces/dashboard | AGPL-3.0 | FLAG / legal review before adoption |

## Initial Adopted Dependency Records

These are proposed V1 or near-V1 dependencies. "Adopted" here means "recommended for first implementation after approval," not yet implemented.

| Project | Purpose | License | Source repository | Release cadence / maintenance | Operational role | We rely on | We do not rely on |
|---|---|---|---|---|---|---|---|
| Temporal | Durable WorkItem workflows | MIT | https://github.com/temporalio/temporal | Active releases; active commercial and OSS community | Owns workflow durability, retries, timers, human wait states | Durable orchestration semantics and SDKs | Policy decisions, CI, security, deployment authority |
| OPA | Deterministic policy decisions | Apache-2.0 | https://github.com/open-policy-agent/opa | CNCF graduated; active | Evaluates scope/risk/approval policy | Policy evaluation over trusted facts | Generating facts, interpreting untrusted evidence, replacing human authority |
| OpenTelemetry | Control-plane telemetry standard | Apache-2.0 | https://github.com/open-telemetry/opentelemetry-collector and language SDKs | CNCF graduated in 2026; very active ecosystem | Standardizes traces, metrics, logs | Vendor-neutral instrumentation | Storage, dashboards, policy, alert semantics |
| Prometheus / Alertmanager | Metrics and alert routing | Apache-2.0 | https://github.com/prometheus/prometheus, https://github.com/prometheus/alertmanager | CNCF graduated; active | V1 metrics/alerts | Metrics collection and alert delivery | Long-term log/trace storage, final deployment authorization |
| Trivy | Security scanning | Apache-2.0 | https://github.com/aquasecurity/trivy | Active, widely used | Vulnerability/config/secret/IaC scanning gate | Scanner output as evidence | Treating scanner output as complete truth |
| Syft | SBOM generation | Apache-2.0 | https://github.com/anchore/syft | Active Anchore project | SBOM generation | Package inventory evidence | Vulnerability adjudication |
| Grype | Vulnerability scanning | Apache-2.0 | https://github.com/anchore/grype | Active Anchore project | Vulnerability cross-check | SBOM/image vulnerability evidence | Sole security authority |
| One coding agent backend, TBD | Sandboxed patch generation | MIT or Apache-2.0 depending choice | OpenHands, SWE-agent/mini-SWE-agent, or Aider repositories | All candidates active enough for V1 POC | Produces patches/tests in sandbox | Investigation and patch proposals | Authority, production access, policy, merge/deploy decisions |

## C. Build vs Integrate Matrix

| Capability | Decision | Reason |
|---|---|---|
| WorkItem durable lifecycle | BUILD thin domain model on Temporal | WorkItem is product-specific; durability should be integrated |
| Workflow engine | INTEGRATE Temporal | Mature durable execution; avoid reimplementation |
| Coding agent | WRAP OpenHands, SWE-agent/mini-SWE-agent, or Aider | Agents are replaceable workers, not trusted control plane |
| Sandboxed execution | WRAP existing container/runtime isolation; evaluate SWE-ReX | Need controlled worker environments; avoid custom runtime |
| Policy language/engine | INTEGRATE OPA | Deterministic, testable policy |
| CI | INTEGRATE existing CI provider initially | V1 should not build CI |
| Security scans | INTEGRATE Trivy, Syft, Grype, secret scanner | Deterministic gates |
| Architecture checks | BUILD repo-specific check harness | Invariants are product-specific, but run as normal tests |
| Git/PR operations | WRAP GitHub/GitLab APIs | Avoid custom Git implementation |
| Observability standard | INTEGRATE OpenTelemetry | Future-proof telemetry |
| Metrics/alerts | INTEGRATE Prometheus/Alertmanager | Mature |
| Log/trace backend | DEFER | License and ops tradeoffs need deeper study |
| Deployment | DEFER Argo CD/Rollouts integration | No production deployment in V1 |
| Feature flags | DEFER OpenFeature/flagd | Useful later; not essential to V1 |
| Secrets manager | DEFER OpenBao | V1 should avoid production secrets |
| IaC | DEFER OpenTofu | Needed later for self-hosted deployment |
| Artifact signing/provenance | EXTEND toward Sigstore/SLSA | Design now; enforce later |
| UI/dashboard | DEFER | Decision model before dashboard |
| Agent framework | REJECT building a generic one | Product is control plane, not agent framework |

## D. Trust Boundaries

The trusted control layer owns authorization context. The LLM owns suggestions only.

Boundaries:

- Human input: untrusted content; may request work but cannot grant hidden authority.
- External docs/websites/emails/logs/issues/repository content: untrusted data; never executable instruction.
- LLM agent: untrusted proposer; may read scoped data and operate in a sandbox.
- Sandbox: untrusted execution result producer; can produce patches, logs, test output, and evidence.
- Git/PR: durable review artifact; not automatically production-authorized.
- CI: deterministic verification boundary; must run from clean checkout and pinned actions/tools.
- Policy engine: deterministic authority boundary; evaluates normalized facts and evidence.
- Secrets manager: privileged boundary; access only via scoped, audited, short-lived identities.
- Build/signing system: trusted artifact boundary; produces versioned, signed artifacts.
- Staging/canary/prod: environment boundaries with increasing authority and stricter gates.
- Observability systems: evidence source; metrics/logs may be incomplete or poisoned and require provenance.

Critical invariant:

`DATA READ BY AN AGENT != AUTHORIZED INSTRUCTION`

## E. Authority Model

| Action | LLM agent | Sandbox worker | CI | Policy engine | Human approver | Deployment controller |
|---|---:|---:|---:|---:|---:|---:|
| Read allowed repo paths | Propose/read via scoped checkout | Yes | Yes | No | On demand | No |
| Read telemetry references | Scoped summaries only | Scoped | Yes, if needed | Receives facts | Yes | No |
| Write code | Sandbox only | Yes | No | No | No | No |
| Write main branch | No | No | No | No | Via merge approval | No |
| Open PR | Via wrapper after checks | Yes, mediated | No | No | No | No |
| Merge PR | No | No | No | Allow/deny only | Yes for V1 | No |
| Build artifact | No | No | Yes | No | No | No |
| Sign artifact | No | No | Yes, via signing identity | No | No | No |
| Deploy staging | No | No | No | Allow/deny later | Approve later | Yes later |
| Deploy production | No | No | No | Allow/deny | Required for high risk | Yes later |
| Rollback | Recommend only | No | No | Allow/deny | Required depending risk | Yes |
| Access secrets | No standing access | No production secrets | Scoped CI secrets | No | No direct secret read | Scoped workload identity |
| Modify policy | Propose PR only | Sandbox only | Test only | No self-modification | Required | No |

V1 rule: all merges require human review, even if the policy engine says "eligible".

## F. WorkItem Lifecycle

Candidate lifecycle:

1. Intake: receive human prompt, GitHub issue, alert, support message, dependency/CVE notice, or provider change.
2. Normalize: create WorkItem with source, type, severity, summary, evidence refs, affected systems, confidence, risk class, allowed/prohibited scope, required verification, required approvals, state, and audit trail.
3. Triage: classify as bug, feature, incident, dependency/security, provider change, or unknown.
4. Scope: compute allowed paths/tools/environments and forbidden paths/tools/environments.
5. Investigate: agent reads only scoped repo and evidence; outputs findings with citations.
6. Plan: agent proposes steps, verification strategy, and risk.
7. Authorize execution: deterministic policy decides whether sandbox work is allowed.
8. Execute in sandbox: agent modifies code and creates tests.
9. Verify: run regression tests, architecture checks, security checks, lint/build.
10. Package evidence: before/after test evidence, diff summary, risk classification, residual uncertainty.
11. Open PR: attach WorkItem, evidence, policy decision, and rollback notes if applicable.
12. Human review: approve, reject, request more investigation.
13. Close: accepted, rejected, duplicate, no-repro, external/provider issue, or deferred.
14. Learn: update eval cases, incident history, provider assumptions, and architecture rules through reviewable PRs.

No autonomous production fix is allowed without reproduction unless a narrow exception is configured, such as deterministic compilation failure.

## G. Risk / Approval Model

Initial risk dimensions:

- Blast radius: docs/test-only, local module, service, shared library, platform-wide, production data.
- Reversibility: trivial revert, normal rollback, migration rollback, irreversible.
- Security sensitivity: none, auth/session, secrets, permissions, cryptography, policy.
- Data sensitivity: no data, non-sensitive data, PII, financial, credentials.
- Verification strength: no repro, repro only, regression test, full CI, staging/canary evidence.
- Change type: docs, tests, config, code, dependency, schema, infrastructure, deployment.
- Confidence: evidence-backed, inferred, speculative.

Initial classes:

- LOW: docs, tests, fixtures, narrow parser fix with regression test. V1: human merge required.
- MEDIUM: adapter logic, retries, serialization, non-destructive config, auth refresh. V1: human merge required plus stronger tests.
- HIGH: shared contracts, auth architecture, permissions, database schema, idempotency, billing, secrets, deployment infrastructure. V1: mandatory human review and likely multiple reviewers.
- CRITICAL: production credentials, destructive production operations, irreversible data loss, privilege escalation, policy bypass. V1: no autonomous execution; investigation only unless explicitly authorized by a human outside the agent.

Approval output should be a structured decision:

- `allowed`: true/false
- `required_approvals`
- `required_checks`
- `blocked_reasons`
- `allowed_scope`
- `forbidden_scope`
- `expires_at`
- `policy_version`

## H. Incident Workflow

Initial incident flow:

1. Alert arrives with metric/log/trace evidence.
2. Correlate recent deploys, dependency changes, provider status, secrets/config changes, and related WorkItems.
3. Determine customer impact and severity.
4. Classify: our bug, provider bug, provider outage, configuration, credential, security, expected failure, unknown.
5. If not clearly our code, do not start code modification by default.
6. If our code is suspected, attempt reproduction in sandbox or staging-like environment.
7. If reproduced, create fix plan and regression test.
8. If not reproduced, produce investigation report and recommended human action.
9. For later autonomy levels, deployment requires staging/canary health evidence and rollback plan.

V1 incident value can be investigation reports and PRs only.

## I. Deployment Safety Model

Long-term required path:

`SOURCE -> CI -> TEST -> SECURITY -> BUILD -> SBOM -> SIGN -> PROVENANCE -> STAGING -> HEALTH CHECK -> CANARY -> METRIC EVALUATION -> PROMOTE OR ROLLBACK`

Rules:

- No SSH patching.
- No editing running production containers.
- No direct production mutation by coding agents.
- No unsigned or unverifiable artifact reaches production.
- No rollout without health criteria.
- No production rollout without rollback path.
- No high-risk rollout without human approval.

V1 does not deploy. It must, however, structure PR evidence so later deployment gates can consume it.

## J. Observability Model

For autonomous operations to be credible, the system must observe:

- WorkItem state transitions and policy decisions.
- Agent runs, prompts, tool calls, model identity, sandbox identity, and token/cost usage.
- Repository checkout, base commit, diff, test commands, exit codes, and artifacts.
- CI checks, security scanner versions, SBOM hash, artifact digest, signature, provenance.
- Incident evidence: alerts, metrics, logs, traces, deploy correlation, provider status.
- Deployment health criteria: SLOs, error rates, latency, saturation, business KPIs, rollback triggers.
- Human decisions: approver, decision, timestamp, evidence reviewed, policy version.

Use OpenTelemetry for control-plane traces/metrics/logs where possible. Prometheus/Alertmanager can provide metrics and alerts. LLM-specific observability may be Langfuse OSS or a thin OpenTelemetry-based run log until needs are clearer.

## K. Data Model Candidates

Candidate concepts only:

- WorkItem
- Signal
- EvidenceRef
- InvestigationRun
- AgentRun
- SandboxSession
- ScopeGrant
- PolicyDecision
- RiskAssessment
- VerificationRun
- PullRequestRef
- HumanDecision
- DeploymentCandidate
- RolloutObservation
- Incident
- ProviderAssumption
- ArchitectureInvariant
- AuditEvent

Potential WorkItem fields:

- `id`
- `source`
- `type`
- `severity`
- `summary`
- `evidence_refs`
- `affected_systems`
- `suspected_ownership`
- `confidence`
- `risk_class`
- `allowed_scope`
- `prohibited_scope`
- `required_verification`
- `required_approvals`
- `current_state`
- `audit_trail`

Do not freeze this schema yet.

## L. Threat Model

| Threat | Initial mitigation |
|---|---|
| Prompt injection from issues, docs, logs, emails, websites | Treat all read text as untrusted data; trusted instructions come only from control layer |
| Poisoned repository content | Scope grants; sandbox-only execution; CI from clean checkout; no repo-controlled widening of authority |
| Malicious dependency | Lockfiles, SBOM, vulnerability scanning, provenance checks, dependency update policy |
| Compromised upstream docs | Require source attribution and confidence; unverifiable claims cannot authorize changes |
| Secret exfiltration | No production secrets in agent sandbox; short-lived scoped credentials; audited secret access |
| Privilege escalation | Separate identities by role; policy engine outside LLM; deny self-modifying authorization |
| CI compromise | Pin actions/tools, verify provenance, protected branches/environments, least-privileged tokens |
| Artifact substitution | Signed artifacts, digest pinning, provenance verification before deploy |
| Unsafe rollback | Rollback plan required; test rollback where possible; schema changes classified high/critical |
| Runaway agents | Budget limits, wall-clock limits, tool allowlists, kill switch, audit events |
| Cost explosion | Per-WorkItem budgets, model routing, token accounting, queue limits |
| Scanner false positives/negatives | Cross-check scanners; human review for ambiguous/high findings |
| Policy bypass through generated code | Architecture checks and policy tests run outside agent authority |
| Data poisoning in observability | Correlate multiple evidence sources; record source provenance and confidence |

## M. Minimum V1

Smallest useful V1:

`GitHub Issue or human prompt -> Temporal workflow -> scoped WorkItem -> sandboxed coding agent -> repo inspection -> patch + regression test -> deterministic checks -> security scans -> PR -> human review`

V1 components:

- Temporal workflow skeleton for WorkItem lifecycle.
- Minimal WorkItem store.
- Git provider adapter for reading issue/prompt context and opening PRs.
- One wrapped coding agent backend, initially selected by proof-of-concept: mini-SWE-agent/SWE-agent, OpenHands headless, or Aider.
- Sandbox runner with path/tool/env allowlists.
- Verification runner for repo tests, lint/build, architecture checks, Trivy/Syft/Grype where applicable.
- OPA policy checks for execution permission, PR eligibility, and required approvals.
- Evidence bundle attached to PR.
- Audit log.
- No production deployment.
- No production secrets.
- Human review required for all merges.

V1 success criteria:

- Produces a useful PR for a low-risk issue.
- Shows what changed, why, evidence, tests, risk, and residual uncertainty.
- Demonstrates that an injected issue/README/log instruction cannot widen authority.
- Demonstrates that no reproduction blocks autonomous bug-fix PR eligibility unless explicitly excepted.

## N. Explicit Non-Goals

- No autonomous production deployment in V1.
- No custom CI system.
- No custom workflow engine.
- No custom Git implementation.
- No custom metrics/logs/traces database.
- No custom secrets manager.
- No custom policy language.
- No custom Kubernetes deployment controller.
- No custom SBOM or signing format.
- No unrestricted production credentials for LLMs.
- No dashboard before decision model.
- No generic multi-agent framework.
- No AI executive persona.
- No auto-merge of high-risk changes.
- No architecture-policy changes without human review.

## O. Open Questions

- Which first agent backend gives the best control-to-capability ratio: mini-SWE-agent/SWE-agent, OpenHands headless, or Aider?
- Should V1 assume GitHub only, or abstract Git providers from day one?
- What database should own WorkItems and audit trails: Postgres likely, but confirm with Temporal persistence and deployment constraints.
- How should evidence bundles be stored: database rows, object storage, Git notes, PR comments, or all of the above?
- How strict should V1 reproduction requirements be for feature requests versus bugs?
- What is the first architecture invariant language: repo-native tests, Semgrep, OPA over metadata, or a combination?
- Which log/trace backend satisfies license policy and operational simplicity?
- Is AGPL acceptable for internal self-hosted observability components?
- How will cost budgets be enforced across model providers?
- What is the human approval identity provider for V1?
- How will policy changes be tested and promoted?
- How much of SLSA should V1 implement versus model as future requirements?
- What are acceptable sandbox isolation technologies on macOS, Linux, and Kubernetes?

## Proposed V1 Implementation Plan

Do not start implementation until this review is approved.

1. Create a repo skeleton with docs, policy, and V1 ADRs.
2. Implement WorkItem lifecycle on Temporal with a local dev profile.
3. Add OPA policies for scope, risk, execution, and PR eligibility.
4. Wrap one coding agent backend behind a narrow interface.
5. Implement sandbox execution with allowlisted commands, paths, time, and cost budget.
6. Implement verification runner and evidence bundle.
7. Integrate GitHub issue input and PR output.
8. Add security scanning gates with pinned tool versions.
9. Add prompt-injection and scope-escape test cases.
10. Stop before deployment automation.

## Sources Reviewed

- Temporal: https://github.com/temporalio/temporal, https://temporal.io/about
- OPA: https://github.com/open-policy-agent/opa, https://www.openpolicyagent.org/docs
- OpenTelemetry graduation: https://www.cncf.io/announcements/2026/05/21/cloud-native-computing-foundation-announces-opentelemetrys-graduation-solidifying-status-as-the-de-facto-observability-standard/
- Prometheus: https://www.cncf.io/announcements/2018/08/09/prometheus-graduates/, https://prometheus.io/docs/introduction/faq/
- Argo: https://www.cncf.io/announcements/2022/12/06/the-cloud-native-computing-foundation-announces-argo-has-graduated/
- OpenFeature: https://www.cncf.io/projects/openfeature/, https://github.com/open-feature
- Trivy: https://github.com/aquasecurity/trivy
- Syft: https://github.com/anchore/syft
- Grype: https://github.com/anchore/grype
- Sigstore/Cosign license policy: https://github.com/sigstore/community/blob/main/LICENSING.md, https://github.com/sigstore/cosign
- SLSA: https://github.com/slsa-framework/slsa, https://slsa.dev
- OpenTofu: https://github.com/opentofu/opentofu, https://github.com/cncf/sandbox/issues/81
- OpenBao: https://github.com/openbao/openbao, https://openbao.org/docs/policies/osps-baseline/
- OpenHands: https://github.com/All-Hands-AI/OpenHands, https://www.openhands.dev/blog/announcing-all-hands-online-beta
- SWE-agent / SWE-ReX / mini-SWE-agent: https://github.com/SWE-agent/SWE-agent, https://github.com/SWE-agent/SWE-ReX, https://pypi.org/project/mini-swe-agent/
- Aider: https://github.com/Aider-AI/aider, https://formulae.brew.sh/formula/aider
- Langfuse: https://github.com/langfuse/langfuse, https://langfuse.com/handbook/chapters/open-source
- Phoenix: https://github.com/Arize-ai/phoenix
- Grafana relicensing: https://grafana.com/blog/grafana-loki-tempo-relicensing-to-agplv3/
