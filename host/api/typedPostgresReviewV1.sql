-- PostgreSQL migration REVIEW ONLY; no live DDL executed or authorized.
-- Preserve sourceRef/taskId/scopeId, index sequence, use JSONB for AI manifest.
-- Use BIGINT for int64 and fixed-scaled exact values; DOUBLE PRECISION for samples only.
-- Use BOOLEAN NULL for explicit unknown. TIMESTAMPTZ for observedAt.
-- Requires backup, authenticated pgAdmin4, least-privilege migration and exact CAST/Crown review.
CREATE TABLE streamEvent (
  eventId TEXT PRIMARY KEY,taskId TEXT NOT NULL,sourceRef CHAR(40) NOT NULL,
  scopeId TEXT NOT NULL,workerId TEXT NOT NULL,sequenceId BIGINT UNIQUE NOT NULL,
  eighthNote SMALLINT NOT NULL CHECK(eighthNote BETWEEN 1 AND 8),
  observedAt TIMESTAMPTZ NOT NULL,evidenceRef TEXT
);
CREATE INDEX eventTaskOrder ON streamEvent(taskId,sourceRef,scopeId,sequenceId,eventId);
CREATE TABLE numericStream(
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId), fieldName TEXT NOT NULL,
  valueKind TEXT NOT NULL CHECK(valueKind IN ('integer','float','fixed')),
  integerValue BIGINT,floatValue DOUBLE PRECISION,scaledValue BIGINT,
  decimalScale SMALLINT CHECK(decimalScale BETWEEN 0 AND 9),
  PRIMARY KEY(eventId,fieldName)
);
CREATE TABLE textStream(
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId),fieldName TEXT NOT NULL,
  textValue TEXT NOT NULL CHECK(length(textValue)<=16384),PRIMARY KEY(eventId,fieldName)
);
CREATE TABLE booleanStream(
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId),fieldName TEXT NOT NULL,
  booleanValue BOOLEAN,PRIMARY KEY(eventId,fieldName)
);
CREATE TABLE aiManifestStream(
  eventId TEXT PRIMARY KEY REFERENCES streamEvent(eventId),manifestJson JSONB NOT NULL,
  manifestSchema TEXT NOT NULL,providerId TEXT NOT NULL,capabilityId TEXT NOT NULL,
  mutationAuthority BOOLEAN NOT NULL DEFAULT FALSE CHECK(mutationAuthority=FALSE),
  greenAuthority BOOLEAN NOT NULL DEFAULT FALSE CHECK(greenAuthority=FALSE),
  crownAuthority BOOLEAN NOT NULL DEFAULT FALSE CHECK(crownAuthority=FALSE)
);