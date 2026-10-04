from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TelemetrySink:
    spans: list[str] = field(default_factory=list)

    def span(self, name: str) -> None:
        self.spans.append(name)

