from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthCriteria:
    max_error_rate: float = 0.01
    max_latency_ms: float = 250.0
    min_availability: float = 0.99
    max_restart_rate: float = 0.01
    max_cpu_saturation: float = 0.85
    minimum_sample_size: int = 100


@dataclass(frozen=True)
class HealthSample:
    error_rate: float
    latency_ms: float
    availability: float
    restart_rate: float
    cpu_saturation: float
    sample_size: int


@dataclass(frozen=True)
class HealthDecision:
    healthy: bool
    reasons: tuple[str, ...]


class HealthEvaluator:
    def evaluate(self, sample: HealthSample, criteria: HealthCriteria) -> HealthDecision:
        reasons: list[str] = []
        if sample.sample_size < criteria.minimum_sample_size:
            reasons.append("insufficient sample size")
        if sample.error_rate > criteria.max_error_rate:
            reasons.append("error rate above threshold")
        if sample.latency_ms > criteria.max_latency_ms:
            reasons.append("latency above threshold")
        if sample.availability < criteria.min_availability:
            reasons.append("availability below threshold")
        if sample.restart_rate > criteria.max_restart_rate:
            reasons.append("restart rate above threshold")
        if sample.cpu_saturation > criteria.max_cpu_saturation:
            reasons.append("cpu saturation above threshold")
        return HealthDecision(not reasons, tuple(reasons))

