from __future__ import annotations

from dataclasses import dataclass

from control_plane.agents.backend import AgentBackend, FixtureParserAgent
from control_plane.builds.supply_chain import Artifact, BuildService
from control_plane.deployment.controller import DeploymentController
from control_plane.domain import Permission, PolicyAction, ScopeGrant, Signal, WorkItem, WorkItemState
from control_plane.git.provider import InMemoryGitHub
from control_plane.health.evaluator import HealthCriteria, HealthSample
from control_plane.policy.engine import LocalPolicyEngine
from control_plane.risk.model import assess_risk
from control_plane.sandbox.runner import SandboxRunner
from control_plane.signals.ingest import classify_incident, normalize
from control_plane.verification.runner import VerificationRunner, apply_patch
from control_plane.workitems.lifecycle import transition


@dataclass(frozen=True)
class WorkflowOutcome:
    item: WorkItem
    repo: dict[str, str]
    artifact: Artifact | None
    production_human_required: bool
    rolled_back: bool


class V2Workflow:
    def __init__(
        self,
        *,
        agent: AgentBackend | None = None,
        policy: LocalPolicyEngine | None = None,
        git: InMemoryGitHub | None = None,
        builder: BuildService | None = None,
        deployment: DeploymentController | None = None,
    ):
        self.agent = agent or FixtureParserAgent()
        self.policy = policy or LocalPolicyEngine()
        self.git = git or InMemoryGitHub()
        self.builder = builder or BuildService()
        self.deployment = deployment or DeploymentController()
        self.verifier = VerificationRunner()

    def run_remediation(
        self,
        signal: Signal,
        repo: dict[str, str],
        *,
        allow_production: bool = False,
        staging_sample: HealthSample | None = None,
        canary_samples: tuple[HealthSample, ...] = (),
        source_commit: str = "fixture-commit",
    ) -> WorkflowOutcome:
        item = normalize(signal)
        artifact: Artifact | None = None
        production_human_required = False
        rolled_back = False

        transition(item, WorkItemState.TRIAGED, "triage started")
        item.incident_class = classify_incident(item)
        transition(item, WorkItemState.SCOPED, f"classified {item.incident_class.value}")

        item.scope = ScopeGrant(
            allowed_paths=("service/parser.py", "tests"),
            forbidden_paths=("policy/", "deploy/production", "src/control_plane/policy"),
            allowed_tools=("python-test", "security-scan", "sbom"),
            forbidden_tools=("git-merge", "deploy-production", "secret-read"),
            allowed_environments=("sandbox", "ci", "staging", "canary"),
            maximum_blast_radius="fixture-service",
        )
        item.risk = assess_risk(signal)
        item.policy_decision = self.policy.decide(item.risk, item.scope)
        item.policy_decision.assert_allowed(PolicyAction.INVESTIGATE)
        transition(item, WorkItemState.AUTHORIZED_FOR_INVESTIGATION, "policy allowed investigation")
        transition(item, WorkItemState.INVESTIGATING, "investigation started")
        item.evidence.append("recent release touched service/parser.py")
        transition(item, WorkItemState.INVESTIGATION_COMPLETE, "investigation complete")

        transition(item, WorkItemState.PLANNED, "plan generated")
        item.policy_decision.assert_allowed(PolicyAction.EXECUTE_SANDBOX)
        transition(item, WorkItemState.AUTHORIZED_FOR_EXECUTION, "policy allowed sandbox execution")
        transition(item, WorkItemState.EXECUTING, "sandbox execution started")

        sandbox_result = SandboxRunner(self.agent).execute(item, repo, item.scope)
        if not sandbox_result.allowed:
            item.evidence.append(f"scope violations: {sandbox_result.violations}")
            transition(item, WorkItemState.BLOCKED, "sandbox diff exceeded scope")
            transition(item, WorkItemState.ESCALATED, "scope violation requires human decision")
            return WorkflowOutcome(item, repo, None, False, False)

        transition(item, WorkItemState.VERIFYING, "independent verification started")
        verification = self.verifier.verify(repo, sandbox_result.patch, sandbox_result.changed_paths)
        item.evidence.append(verification.output_ref)
        if not verification.passed:
            transition(item, WorkItemState.BLOCKED, "verification failed")
            transition(item, WorkItemState.ESCALATED, "verification failure requires human")
            return WorkflowOutcome(item, repo, None, False, False)

        item.policy_decision = self.policy.decide(item.risk, item.scope, verification_passed=True)
        transition(item, WorkItemState.VERIFIED, "verification passed")

        item.policy_decision.assert_allowed(PolicyAction.OPEN_PR)
        pr = self.git.open_pr(item.summary, sandbox_result.changed_paths)
        item.pr_id = pr.id
        transition(item, WorkItemState.PR_READY, f"pr opened {pr.id}")
        transition(item, WorkItemState.AWAITING_MERGE_AUTHORIZATION, "merge authorization required")
        if item.policy_decision.permission_for(PolicyAction.AUTO_MERGE) != Permission.ALLOW:
            transition(item, WorkItemState.ESCALATED, "auto-merge not authorized")
            return WorkflowOutcome(item, repo, None, False, False)

        self.git.merge(pr.id)
        repo = apply_patch(repo, sandbox_result.patch)
        transition(item, WorkItemState.MERGED, "control plane merged PR")

        transition(item, WorkItemState.BUILDING, "clean build started")
        artifact = self.builder.build(repo, source_commit, verification.sbom_hash)
        item.release_id = artifact.id
        item.evidence.append(f"artifact:{artifact.digest}")
        transition(item, WorkItemState.BUILD_VERIFIED, "artifact built, signed, provenance recorded")

        item.policy_decision.assert_allowed(PolicyAction.DEPLOY_STAGING)
        transition(item, WorkItemState.STAGING, "deploying immutable artifact to staging")
        self.deployment.deploy_staging(artifact)
        transition(item, WorkItemState.STAGING_OBSERVING, "staging observing")
        criteria = HealthCriteria()
        staging_health = self.deployment.observe_staging(staging_sample or healthy_sample(), criteria)
        if not staging_health.healthy:
            transition(item, WorkItemState.ROLLING_BACK, f"staging unhealthy: {staging_health.reasons}")
            rolled_back = self.deployment.rollback()
            transition(item, WorkItemState.ROLLED_BACK if rolled_back else WorkItemState.FAILED, "staging rollback complete")
            return WorkflowOutcome(item, repo, artifact, False, rolled_back)

        item.policy_decision.assert_allowed(PolicyAction.DEPLOY_CANARY)
        for fraction, sample in zip((5, 25, 50, 100), canary_samples or (healthy_sample(), healthy_sample(), healthy_sample(), healthy_sample())):
            if item.state == WorkItemState.STAGING_OBSERVING:
                transition(item, WorkItemState.CANARY, f"starting {fraction}% canary")
            else:
                transition(item, WorkItemState.CANARY, f"continuing {fraction}% canary")
            self.deployment.start_canary(artifact, fraction) if fraction == 5 else self.deployment.promote_canary(fraction)
            transition(item, WorkItemState.CANARY_OBSERVING, f"observing {fraction}% canary")
            health = self.deployment.observe_canary(sample, criteria)
            if not health.healthy:
                transition(item, WorkItemState.ROLLING_BACK, f"canary unhealthy: {health.reasons}")
                rolled_back = self.deployment.rollback()
                transition(item, WorkItemState.ROLLED_BACK if rolled_back else WorkItemState.FAILED, "canary rollback complete")
                return WorkflowOutcome(item, repo, artifact, False, rolled_back)

        production_permission = item.policy_decision.permission_for(PolicyAction.DEPLOY_PRODUCTION)
        if not allow_production or production_permission != Permission.ALLOW:
            production_human_required = True
            transition(item, WorkItemState.ESCALATED, "production promotion requires human approval")
            return WorkflowOutcome(item, repo, artifact, production_human_required, rolled_back)

        transition(item, WorkItemState.PRODUCTION, "promoting to production")
        transition(item, WorkItemState.PRODUCTION_OBSERVING, "production observing")
        transition(item, WorkItemState.CLOSED, "production observation healthy")
        return WorkflowOutcome(item, repo, artifact, production_human_required, rolled_back)


def healthy_sample() -> HealthSample:
    return HealthSample(
        error_rate=0.0,
        latency_ms=80.0,
        availability=1.0,
        restart_rate=0.0,
        cpu_saturation=0.25,
        sample_size=500,
    )


def degraded_sample() -> HealthSample:
    return HealthSample(
        error_rate=0.05,
        latency_ms=420.0,
        availability=0.95,
        restart_rate=0.0,
        cpu_saturation=0.45,
        sample_size=500,
    )

