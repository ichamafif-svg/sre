CREATE TABLE IF NOT EXISTS work_items (
    id TEXT PRIMARY KEY,
    signal_id TEXT NOT NULL,
    signal_kind TEXT NOT NULL,
    signal_source TEXT NOT NULL,
    summary TEXT NOT NULL,
    state TEXT NOT NULL,
    incident_class TEXT NOT NULL,
    risk_class TEXT,
    pr_id TEXT,
    release_id TEXT,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS policy_decisions (
    id BIGSERIAL PRIMARY KEY,
    work_item_id TEXT NOT NULL REFERENCES work_items(id),
    policy_version TEXT NOT NULL,
    permissions JSONB NOT NULL,
    required_human_actions JSONB NOT NULL,
    blocked_reasons JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    work_item_id TEXT NOT NULL REFERENCES work_items(id),
    event TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (work_item_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS evidence_metadata (
    id BIGSERIAL PRIMARY KEY,
    work_item_id TEXT NOT NULL REFERENCES work_items(id),
    evidence_ref TEXT NOT NULL,
    kind TEXT NOT NULL,
    digest TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (work_item_id, evidence_ref)
);

CREATE TABLE IF NOT EXISTS external_mutations (
    idempotency_key TEXT PRIMARY KEY,
    work_item_id TEXT NOT NULL REFERENCES work_items(id),
    operation TEXT NOT NULL,
    external_ref TEXT,
    status TEXT NOT NULL,
    outcome JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_work_items_state ON work_items(state);
CREATE INDEX IF NOT EXISTS idx_audit_events_work_item ON audit_events(work_item_id);
CREATE INDEX IF NOT EXISTS idx_evidence_work_item ON evidence_metadata(work_item_id);

