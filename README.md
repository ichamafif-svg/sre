# Autonomous SRE Control Plane

Production-shaped V2 scaffold for a self-hosted software operations control plane.

The current implementation is a local vertical slice with deterministic adapters. It models the full loop from signal to WorkItem, sandboxed patch, independent verification, PR, policy-controlled auto-merge, immutable artifact, staging, canary, rollback, and human-gated production promotion.

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Key docs:

- `docs/architecture/INITIAL_ARCHITECTURE_REVIEW.md`
- `docs/adr/0001-v2-shaped-modular-monolith.md`
- `docs/operations/V2_IMPLEMENTATION_REPORT.md`

