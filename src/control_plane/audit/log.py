from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AuditLog:
    events: list[str] = field(default_factory=list)

    def append(self, event: str) -> None:
        self.events.append(event)

