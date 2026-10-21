-- LuHm OS: SQLite STRICT local stub only, never live production DDL.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS streamEvent(
  eventId TEXT PRIMARY KEY,taskId TEXT NOT NULL,sourceRef TEXT NOT NULL CHECK(length(sourceRef)=40 AND sourceRef NOT GLOB '*[^0-9a-f]*'),
  scopeId TEXT NOT NULL,workerId TEXT NOT NULL,sequenceId INTEGER UNIQUE NOT NULL CHECK(sequenceId>=0),
  eighthNote INTEGER NOT NULL CHECK(eighthNote BETWEEN 1 AND 8),observedAt TEXT NOT NULL CHECK(length(observedAt) BETWEEN 20 AND 40 AND substr(observedAt,-1)='Z'),
  evidenceRef TEXT
) STRICT;
CREATE INDEX IF NOT EXISTS eventTaskOrder ON streamEvent(taskId,sourceRef,scopeId,sequenceId,eventId);
CREATE TABLE IF NOT EXISTS numericStream(
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId),fieldName TEXT NOT NULL,
  valueKind TEXT NOT NULL CHECK(valueKind IN ('integer','float','fixed')),
  integerValue INTEGER,floatValue REAL,scaledValue INTEGER,decimalScale INTEGER CHECK(decimalScale BETWEEN 0 AND 9),
  PRIMARY KEY(eventId,fieldName),
  CHECK((valueKind='integer' AND integerValue IS NOT NULL AND floatValue IS NULL AND scaledValue IS NULL AND decimalScale IS NULL)
     OR (valueKind='float' AND floatValue IS NOT NULL AND integerValue IS NULL AND scaledValue IS NULL AND decimalScale IS NULL)
     OR (valueKind='fixed' AND scaledValue IS NOT NULL AND decimalScale IS NOT NULL AND integerValue IS NULL AND floatValue IS NULL))
) STRICT;
CREATE INDEX IF NOT EXISTS numericSortInteger ON numericStream(fieldName,integerValue,eventId) WHERE valueKind='integer';
CREATE INDEX IF NOT EXISTS numericSortFloat ON numericStream(fieldName,floatValue,eventId) WHERE valueKind='float';
CREATE INDEX IF NOT EXISTS numericSortFixed ON numericStream(fieldName,decimalScale,scaledValue,eventId) WHERE valueKind='fixed';
CREATE TABLE IF NOT EXISTS textStream(
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId),fieldName TEXT NOT NULL,
  textValue TEXT NOT NULL CHECK(length(textValue)<=16384),PRIMARY KEY(eventId,fieldName)
) STRICT;
CREATE INDEX IF NOT EXISTS textSort ON textStream(fieldName,textValue COLLATE BINARY,eventId);
CREATE TABLE IF NOT EXISTS booleanStream(
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId),fieldName TEXT NOT NULL,
  booleanValue INTEGER CHECK(booleanValue IN (0,1) OR booleanValue IS NULL),
  PRIMARY KEY(eventId,fieldName)
) STRICT;
CREATE INDEX IF NOT EXISTS booleanSort ON booleanStream(fieldName,booleanValue,eventId);
CREATE TABLE IF NOT EXISTS aiManifestStream(
  eventId TEXT PRIMARY KEY REFERENCES streamEvent(eventId),manifestJson TEXT NOT NULL CHECK(json_valid(manifestJson)),
  manifestSchema TEXT NOT NULL,providerId TEXT NOT NULL,capabilityId TEXT NOT NULL,
  mutationAuthority INTEGER NOT NULL DEFAULT 0 CHECK(mutationAuthority=0),
  greenAuthority INTEGER NOT NULL DEFAULT 0 CHECK(greenAuthority=0),
  crownAuthority INTEGER NOT NULL DEFAULT 0 CHECK(crownAuthority=0)
) STRICT;
CREATE INDEX IF NOT EXISTS manifestRoute ON aiManifestStream(providerId,capabilityId,eventId);
CREATE TABLE IF NOT EXISTS artifactPointer(
  artifactId TEXT PRIMARY KEY,eventId TEXT NOT NULL REFERENCES streamEvent(eventId),
  fileName TEXT NOT NULL,sha256 TEXT NOT NULL CHECK(length(sha256)=64 AND sha256 NOT GLOB '*[^0-9a-f]*'),
  storageLane TEXT NOT NULL CHECK(storageLane IN ('githubSource','chatLibraryCache','googleDriveDurable')),
  logicalFileRef TEXT NOT NULL,sizeBytes INTEGER NOT NULL CHECK(sizeBytes>=0)
) STRICT;
CREATE INDEX IF NOT EXISTS artifactEvent ON artifactPointer(eventId,storageLane);
