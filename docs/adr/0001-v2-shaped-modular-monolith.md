# ADR 0001: V2-Shaped Modular Monolith

Date: 2026-10-04

## Status

Accepted for initial implementation.

## Context

The control plane must support the full V2 loop from prompt/issue/alert through WorkItem, sandboxed remediation, verification, policy-driven merge, staging, canary, promotion or rollback, and observation. Autonomy must be policy-disabled where controls are not yet proven.

## Decision

Start as a Python modular monolith with explicit ports for:

- agent backend
- policy engine
- Git provider
- build/sign/provenance
- deployment controller
- health evaluator
- evidence/audit/telemetry stores

Use deterministic local adapters for the first vertical slice, while preserving boundaries for Temporal, PostgreSQL, OPA, GitHub, Cosign/SLSA, and Argo-style deployment integrations.

## Consequences

The first implementation can run without external credentials and can test authority boundaries quickly. It does not yet prove operational hardening for real infrastructure. Production autonomy remains disabled by policy and by missing live integrations.

