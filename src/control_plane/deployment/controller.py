from __future__ import annotations

from dataclasses import dataclass, field

from control_plane.builds.supply_chain import Artifact
from control_plane.health.evaluator import HealthCriteria, HealthDecision, HealthEvaluator, HealthSample


@dataclass
class EnvironmentState:
    name: str
    current_artifact: Artifact | None = None
    previous_known_good: Artifact | None = None
    canary_fraction: int = 0
    history: list[str] = field(default_factory=list)


class DeploymentController:
    def __init__(self, evaluator: HealthEvaluator | None = None):
        self.evaluator = evaluator or HealthEvaluator()
        self.environments = {
            "staging": EnvironmentState("staging"),
            "production": EnvironmentState("production"),
        }

    def deploy_staging(self, artifact: Artifact) -> None:
        env = self.environments["staging"]
        env.previous_known_good = env.current_artifact
        env.current_artifact = artifact
        env.history.append(f"deploy staging {artifact.digest}")

    def observe_staging(self, sample: HealthSample, criteria: HealthCriteria) -> HealthDecision:
        decision = self.evaluator.evaluate(sample, criteria)
        self.environments["staging"].history.append(f"staging health {decision.healthy}")
        return decision

    def start_canary(self, artifact: Artifact, fraction: int) -> None:
        env = self.environments["production"]
        env.previous_known_good = env.current_artifact
        env.current_artifact = artifact
        env.canary_fraction = fraction
        env.history.append(f"canary {fraction}% {artifact.digest}")

    def promote_canary(self, fraction: int) -> None:
        env = self.environments["production"]
        env.canary_fraction = fraction
        env.history.append(f"promote canary {fraction}%")

    def observe_canary(self, sample: HealthSample, criteria: HealthCriteria) -> HealthDecision:
        decision = self.evaluator.evaluate(sample, criteria)
        self.environments["production"].history.append(f"canary health {decision.healthy}")
        return decision

    def rollback(self) -> bool:
        env = self.environments["production"]
        if env.previous_known_good is None:
            env.history.append("rollback failed: no previous artifact")
            return False
        env.current_artifact = env.previous_known_good
        env.canary_fraction = 0
        env.history.append(f"rollback {env.current_artifact.digest}")
        return True

