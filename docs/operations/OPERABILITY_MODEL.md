# Minimal Operability Model

Date: 2026-10-04

Status: **DESIGN SEED -- NOT FROZEN**

Gate A passed at `REAL_LOCAL`. Gate B is next. Gate C operability modeling has not started as implementation work.

The Software Operations Plane is intended to become a first-class peer of the managed product's business/domain plane, not an external SRE bot bolted onto logs. Future managed products/components should be able to declare operational metadata that the control plane can evaluate deterministically.

The following concepts are candidates only. They are not frozen and are not implemented as product state yet.

## Candidate Concepts

### Component

A managed software unit that can expose an operability contract.

Candidate fields:

- stable component id
- name
- owner
- repository
- source paths
- runtime references

### OperationalContract

Machine-readable contract exposed by a component to the operations plane.

Candidate questions:

- What is this component?
- Who owns it?
- What kind of change is this?
- Is it mutating?
- What risk class applies?
- What telemetry identifies it?
- What health criteria apply?
- What dependencies exist?
- What retry semantics exist?
- What idempotency requirements exist?
- Can outcome be unknown?
- How is it reconciled?
- Can it be rolled back or disabled?
- What is the expected blast radius?

### DependencyReference

A candidate declaration of upstream, downstream, provider, package, service, or runtime dependencies relevant to safe change and recovery.

### HealthContract

A candidate declaration of health signals, service-level expectations, canary checks, and rollback criteria.

### RuntimeReference

A candidate reference to runtime instances, environments, clusters, jobs, or services where a component is observed.

### ReleaseReference

A candidate reference to artifacts, builds, provenance, deployments, feature flags, and release state.

### Lineage References

Candidate stable chain:

```text
WorkItem
-> Investigation
-> AgentRun
-> Commit
-> PR
-> Artifact
-> Release
-> Deployment
-> RuntimeObservation
-> Incident
-> RemediationWorkItem
```

## Status

No schema or enforcement has been added. This is intentionally held until Gate B and later gates provide evidence for which operational metadata is actually needed.
