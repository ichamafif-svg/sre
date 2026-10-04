from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvidenceStore:
    records: dict[str, str] = field(default_factory=dict)

    def put(self, key: str, content: str) -> str:
        ref = f"evidence://{key}"
        self.records[ref] = content
        return ref

