from __future__ import annotations

import hashlib


def stable_idempotency_key(*parts: str) -> str:
    material = "\0".join(parts)
    return hashlib.sha256(material.encode()).hexdigest()

