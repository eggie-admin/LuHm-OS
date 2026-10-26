-- LuHm OS SQL-first operational state, MariaDB source migration proposal only.
-- Apply to an EXISTING Professor-approved local MariaDB database via Unix socket.
-- Do not auto-run from app startup, CI, ChatGPT tools or public web routes.
-- Require backup, minimum DDL rights and independent migration review first.
-- GitHub remains authoritative for source code and reviewed YAML defaults.
-- This table is for bounded operational settings, never passwords, keys or Crown.

CREATE TABLE IF NOT EXISTS luhm_runtime_state (
    namespace VARCHAR(48) NOT NULL,
    state_key VARCHAR(100) NOT NULL,
    value_json LONGTEXT NOT NULL CHECK (JSON_VALID(value_json)),
    status VARCHAR(16) NOT NULL DEFAULT 'active'
       CHECK (status IN ('active', 'revoked')),
    source_sha CHAR(40) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (namespace, state_key)
);

CREATE TABLE IF NOT EXISTS luhm_state_event (
    event_id VARCHAR(80) PRIMARY KEY,
    namespace VARCHAR(48) NOT NULL,
    state_key VARCHAR(100) NOT NULL,
    source_sha CHAR(40) NOT NULL,
    action VARCHAR(24) NOT NULL
       CHECK (action IN ('stage', 'approve', 'update', 'revoke', 'rollback')),
    evidence_ref VARCHAR(250),
    observed_at DATETIME(6) NOT NULL
);

CREATE INDEX luhm_event_key_order
    ON luhm_state_event(namespace, state_key, observed_at, event_id);

-- Read through a scoped application role, not the DDL owner:
-- SELECT value_json, status, source_sha FROM luhm_runtime_state
-- WHERE namespace = ? AND state_key = ?;
-- Syntax of prepared-statement bind markers varies by client. Never concatenate user input.
-- Keep write grants, authentication and signing material entirely outside public MCP.
