from __future__ import annotations

from dataclasses import dataclass

from control_plane.agents.backend import AgentBackend, Patch
from control_plane.domain import ScopeGrant, WorkItem


@dataclass(frozen=True)
class SandboxResult:
    patch: Patch
    changed_paths: tuple[str, ...]
    allowed: bool
    violations: tuple[str, ...]


def _path_allowed(path: str, scope: ScopeGrant) -> bool:
    if any(path.startswith(prefix) for prefix in scope.forbidden_paths):
        return False
    return any(path == allowed or path.startswith(f"{allowed}/") for allowed in scope.allowed_paths)


class SandboxRunner:
    def __init__(self, backend: AgentBackend):
        self.backend = backend

    def execute(self, item: WorkItem, repo: dict[str, str], scope: ScopeGrant) -> SandboxResult:
        patch = self.backend.produce_patch(item, repo, scope)
        changed_paths = tuple(sorted((*patch.changed_files.keys(), *patch.tests_added.keys())))
        violations = tuple(path for path in changed_paths if not _path_allowed(path, scope))
        return SandboxResult(patch, changed_paths, not violations, violations)

