-- CANDIDATE ONLY: existing private MariaDB, SQL-first state.
-- No live migration, public database ports, automatic DDL or JS in SQL.
-- Apply only after a backup, least-privilege review and owner-approved rollout.
-- Caller must mutate its business row AND insert outbox row in ONE transaction.
CREATE TABLE IF NOT EXISTS luhm_duplex_outbox (
  peer_id VARCHAR(80) NOT NULL,
  stream_id INTEGER UNSIGNED NOT NULL,
  sequence_id BIGINT UNSIGNED NOT NULL,
  correlation_id BIGINT UNSIGNED NOT NULL,
  lane TINYINT UNSIGNED NOT NULL CHECK (lane BETWEEN 0 AND 3),
  packet_kind TINYINT UNSIGNED NOT NULL CHECK (packet_kind IN (1,3)),
  payload BLOB NOT NULL,
  payload_sha256 CHAR(64) NOT NULL,
  state VARCHAR(16) NOT NULL CHECK (state IN ('pending','sent','acked','quarantined')),
  attempt_count SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  next_attempt_at DATETIME(6) NOT NULL,
  observed_at DATETIME(6) NOT NULL,
  PRIMARY KEY (peer_id,stream_id,sequence_id)
);
CREATE INDEX luhm_duplex_outbox_due
  ON luhm_duplex_outbox(state,next_attempt_at,attempt_count);

-- Inbound packet goes into dedup ledger before acknowledgement.
CREATE TABLE IF NOT EXISTS luhm_duplex_inbox (
  peer_id VARCHAR(80) NOT NULL,
  stream_id INTEGER UNSIGNED NOT NULL,
  sequence_id BIGINT UNSIGNED NOT NULL,
  correlation_id BIGINT UNSIGNED NOT NULL,
  payload_sha256 CHAR(64) NOT NULL,
  accepted_at DATETIME(6) NOT NULL,
  PRIMARY KEY (peer_id,stream_id,sequence_id)
);

-- Durable resume watermark is scoped to the remote peer AND stream.
CREATE TABLE IF NOT EXISTS luhm_duplex_cursor (
  peer_id VARCHAR(80) NOT NULL,
  stream_id INTEGER UNSIGNED NOT NULL,
  last_received BIGINT UNSIGNED NOT NULL,
  last_acked_outbound BIGINT UNSIGNED NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  PRIMARY KEY (peer_id,stream_id)
);

-- Public MCP does NOT connect to this database; the private adapter uses a
-- narrowly scoped SQL account and parameterized transactions. No secrets here.
-- A database INSERT alone does not send network packets. A separately
-- authorized Python worker and authenticated transport handle delivery.
