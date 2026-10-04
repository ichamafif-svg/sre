from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class PullRequest:
    id: str
    branch: str
    title: str
    changed_paths: tuple[str, ...]
    merged: bool = False


@dataclass
class InMemoryGitHub:
    pull_requests: dict[str, PullRequest] = field(default_factory=dict)

    def open_pr(self, title: str, changed_paths: tuple[str, ...]) -> PullRequest:
        pr = PullRequest(id=str(uuid4()), branch=f"control-plane/{uuid4()}", title=title, changed_paths=changed_paths)
        self.pull_requests[pr.id] = pr
        return pr

    def merge(self, pr_id: str) -> None:
        self.pull_requests[pr_id].merged = True

