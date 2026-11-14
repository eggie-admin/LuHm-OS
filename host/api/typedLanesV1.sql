-- LuHm OS: SQLite STRICT local stub only, never live production DDL.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS streamEvent(
  eventId TEXT PRIMARY KEY CHECK(length(eventId) BETWEEN 1 AND 80),taskId TEXT NOT NULL CHECK(length(taskId) BETWEEN 1 AND 80),
  sourceRef TEXT NOT NULL CHECK(length(sourceRef)=40 AND sourceRef NOT GLOB '*[^0-9a-f]*'),
  scopeId TEXT NOT NULL CHECK(length(scopeId) BETWEEN 1 AND 80),workerId TEXT NOT NULL CHECK(length(workerId) BETWEEN 1 AND 80),
  sequenceId INTEGER UNIQUE NOT NULL CHECK(sequenceId>=0),
  eighthNote INTEGER NOT NULL CHECK(eighthNote BETWEEN 1 AND 8),
  observedAt TEXT NOT NULL CHECK(length(observedAt) BETWEEN 20 AND 40 AND observedAt GLOB '????-??-??T??:??:??*Z'),
  evidenceRef TEXT
) STRICT;
CREATE INDEX IF NOT EXISTS eventTaskOrder ON streamEvent(taskId,sourceRef,scopeId,sequenceId,eventId);
CREATE TABLE IF NOT EXISTS numericStream(
  eventId TEXT NOT NULL REFERENCES streamEvent(eventId),fieldName TEXT NOT NULL,
  valueKind TEXT NOT NULL CHECK(valueKind IN ('integer','float','fixed')),
  integerValue INTEGER,floatValue REAL,scaledValue INTEGER,decimalScale INTEGER CHECK(decimalScale BETWEEN 0 AND 9),
  PRIMARY KEY(eventId,fieldName),
  CHECK((valueKind='integer' AND integerValue IS NOT NULL AND floatValue IS NULL AND scaledValue IS NULL AND decimalScale IS NULL)
     OR (valueKind='float' AND floatValue IS NOT NULL AND floatValue BETWEEN -1.7976931348623157e308 AND 1.7976931348623157e308 AND integerValue IS NULL AND scaledValue IS NULL AND decimalScale IS NULL)
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

-- LamoS audit: keep raw SQL writes aligned with the guarded Python adapter.
-- Local SQLite stub only; never automatically apply this source DDL to production.
CREATE TRIGGER IF NOT EXISTS aiManifestGuardInsert
BEFORE INSERT ON aiManifestStream
BEGIN
  SELECT RAISE(ABORT, 'invalid manifest JSON') WHERE json_valid(NEW.manifestJson) <> 1;
  SELECT RAISE(ABORT, 'AI manifest identity/authority mismatch') WHERE
       json_type(NEW.manifestJson, '$') IS NOT 'object'
    OR NEW.manifestSchema IS NOT 'luhmOs.aiTaskManifest.v2'
    OR json_extract(NEW.manifestJson,'$.schema') IS NOT NEW.manifestSchema
    OR json_extract(NEW.manifestJson,'$.taskId') IS NOT (SELECT taskId FROM streamEvent WHERE eventId=NEW.eventId)
    OR json_extract(NEW.manifestJson,'$.sourceRef') IS NOT (SELECT sourceRef FROM streamEvent WHERE eventId=NEW.eventId)
    OR json_extract(NEW.manifestJson,'$.scopeId') IS NOT (SELECT scopeId FROM streamEvent WHERE eventId=NEW.eventId)
    OR json_extract(NEW.manifestJson,'$.providerId') IS NOT NEW.providerId
    OR json_extract(NEW.manifestJson,'$.capabilityId') IS NOT NEW.capabilityId
    OR json_type(NEW.manifestJson,'$.authority') IS NOT 'object'
    OR json_type(NEW.manifestJson,'$.authority.mutation') IS NOT 'false'
    OR json_type(NEW.manifestJson,'$.authority.green') IS NOT 'false'
    OR json_type(NEW.manifestJson,'$.authority.crown') IS NOT 'false';
END;
CREATE TRIGGER IF NOT EXISTS aiManifestGuardUpdate
BEFORE UPDATE ON aiManifestStream
BEGIN
  SELECT RAISE(ABORT, 'invalid manifest JSON') WHERE json_valid(NEW.manifestJson) <> 1;
  SELECT RAISE(ABORT, 'AI manifest identity/authority mismatch') WHERE
       json_type(NEW.manifestJson, '$') IS NOT 'object'
    OR NEW.manifestSchema IS NOT 'luhmOs.aiTaskManifest.v2'
    OR json_extract(NEW.manifestJson,'$.schema') IS NOT NEW.manifestSchema
    OR json_extract(NEW.manifestJson,'$.taskId') IS NOT (SELECT taskId FROM streamEvent WHERE eventId=NEW.eventId)
    OR json_extract(NEW.manifestJson,'$.sourceRef') IS NOT (SELECT sourceRef FROM streamEvent WHERE eventId=NEW.eventId)
    OR json_extract(NEW.manifestJson,'$.scopeId') IS NOT (SELECT scopeId FROM streamEvent WHERE eventId=NEW.eventId)
    OR json_extract(NEW.manifestJson,'$.providerId') IS NOT NEW.providerId
    OR json_extract(NEW.manifestJson,'$.capabilityId') IS NOT NEW.capabilityId
    OR json_type(NEW.manifestJson,'$.authority') IS NOT 'object'
    OR json_type(NEW.manifestJson,'$.authority.mutation') IS NOT 'false'
    OR json_type(NEW.manifestJson,'$.authority.green') IS NOT 'false'
    OR json_type(NEW.manifestJson,'$.authority.crown') IS NOT 'false';
END;
CREATE TRIGGER IF NOT EXISTS streamEventManifestIdentityFreeze
BEFORE UPDATE OF taskId, sourceRef, scopeId ON streamEvent
WHEN EXISTS(SELECT 1 FROM aiManifestStream WHERE eventId=OLD.eventId)
AND (NEW.taskId IS NOT OLD.taskId OR NEW.sourceRef IS NOT OLD.sourceRef OR NEW.scopeId IS NOT OLD.scopeId)
BEGIN
  SELECT RAISE(ABORT, 'event identity is bound to manifest');
END;
