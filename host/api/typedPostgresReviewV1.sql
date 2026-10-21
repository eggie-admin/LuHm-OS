-- PostgreSQL migration REVIEW ONLY; no live DDL executed or authorized.
-- Preserve sourceRef/taskId/scopeId, index sequence, use JSONB for AI manifest.
-- Use BIGINT for int64 and fixed-scaled exact values; DOUBLE PRECISION for samples only.
-- Use BOOLEAN NULL for explicit unknown. TIMESTAMPTZ for observedAt.
-- Requires backup, authenticated pgAdmin4, least-privilege migration and exact CAST/Crown review.
CREATE TABLE streamEvent (
  eventId TEXT PRIMARY KEY CHECK(length(eventId) BETWEEN 1 AND 80),
  taskId TEXT NOT NULL CHECK(length(taskId) BETWEEN 1 AND 80),
  sourceRef CHAR(40) NOT NULL CHECK(sourceRef ~ '^[0-9a-f]{40}
  scopeId TEXT NOT NULL CHECK(length(scopeId) BETWEEN 1 AND 80),
  workerId TEXT NOT NULL CHECK(length(workerId) BETWEEN 1 AND 80),
  sequenceId BIGINT UNIQUE NOT NULL CHECK(sequenceId>=0),
  eighthNote SMALLINT NOT NULL CHECK(eighthNote BETWEEN 1 AND 8),
  observedAt TIMESTAMPTZ NOT NULL,evidenceRef TEXT
);
CREATE INDEX eventTaskOrder ON streamEvent(taskId,sourceRef,scopeId,sequenceId,eventId);
CREATE TABLE numericStream(
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId), fieldName TEXT NOT NULL,
  valueKind TEXT NOT NULL CHECK(valueKind IN ('integer','float','fixed')),
  integerValue BIGINT,floatValue DOUBLE PRECISION,scaledValue BIGINT,
  decimalScale SMALLINT CHECK(decimalScale BETWEEN 0 AND 9),
  PRIMARY KEY(eventId,fieldName),
  CHECK((valueKind='integer' AND integerValue IS NOT NULL AND floatValue IS NULL AND scaledValue IS NULL AND decimalScale IS NULL)
     OR (valueKind='float' AND floatValue IS NOT NULL AND floatValue > '-Infinity'::float8 AND floatValue < 'Infinity'::float8 AND integerValue IS NULL AND scaledValue IS NULL AND decimalScale IS NULL)
     OR (valueKind='fixed' AND scaledValue IS NOT NULL AND decimalScale IS NOT NULL AND integerValue IS NULL AND floatValue IS NULL))
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
);),
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
-- Source review only. Align artifact provenance with the local STRICT lane.
CREATE TABLE artifactPointer(
  artifactId TEXT PRIMARY KEY,
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId),
  fileName TEXT NOT NULL,
  sha256 CHAR(64) NOT NULL CHECK(sha256 ~ '^[0-9a-f]{64}$'),
  storageLane TEXT NOT NULL CHECK(storageLane IN ('githubSource','chatLibraryCache','googleDriveDurable')),
  logicalFileRef TEXT NOT NULL,
  sizeBytes BIGINT NOT NULL CHECK(sizeBytes>=0)
);
CREATE INDEX artifactEvent ON artifactPointer(eventId,storageLane);
