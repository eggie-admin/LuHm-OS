-- LuHm-OS: one logical Crown proof per task/scope/source. Evidence-by-reference.
-- Offline schema only; never run a migration on a production database from PR CI.
CREATE TABLE IF NOT EXISTS crownProof (
  proofId TEXT PRIMARY KEY,
  taskId TEXT NOT NULL,
  scopeId TEXT NOT NULL,
  sourceRef TEXT NOT NULL CHECK (LENGTH(sourceRef) = 40),
  envelopeJson TEXT NOT NULL CHECK (JSON_VALID(envelopeJson)),
  updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS crownProofSource ON crownProof(sourceRef);
CREATE INDEX IF NOT EXISTS crownProofTask ON crownProof(taskId);
