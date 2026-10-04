from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class Artifact:
    id: str
    source_commit: str
    digest: str
    signature: str
    provenance: dict[str, str]
    sbom_hash: str


class BuildService:
    def build(self, repo: dict[str, str], source_commit: str, sbom_hash: str) -> Artifact:
        material = "\n".join(f"{path}\0{content}" for path, content in sorted(repo.items()))
        digest = hashlib.sha256(material.encode()).hexdigest()
        signature = hashlib.sha256(f"local-dev-signer:{digest}".encode()).hexdigest()
        return Artifact(
            id=f"artifact-{uuid4()}",
            source_commit=source_commit,
            digest=digest,
            signature=signature,
            provenance={
                "builder": "local-build-service",
                "source_commit": source_commit,
                "digest": digest,
                "signing_mode": "local-dev-signature-not-cosign",
            },
            sbom_hash=sbom_hash,
        )

