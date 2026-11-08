-- LuHm-OS machine registry, disposable SQLite STRICT source prototype.
-- Source Canon remains GitHub; SQL is a projection of machine facts/evidence.
-- NEVER migrate/replace a live DB by running this in production.
PRAGMA foreign_keys=ON;

CREATE TABLE sourceRevision (
  sourceRef TEXT PRIMARY KEY CHECK(length(sourceRef)=40 AND sourceRef NOT GLOB '*[^0-9a-f]*'),
  treeDigest TEXT NOT NULL CHECK(length(treeDigest)=64 AND treeDigest NOT GLOB '*[^0-9a-f]*'),
  upstream TEXT NOT NULL CHECK(upstream='eggie-admin/LuHm-OS'),
  recordState TEXT NOT NULL CHECK(recordState IN ('SOURCE_CANDIDATE','REVIEWED','UNKNOWN')),
  observedAt TEXT NOT NULL CHECK(length(observedAt) BETWEEN 20 AND 40 AND observedAt GLOB '????-??-??T??:??:??*Z')
) STRICT;

CREATE TABLE machineIdentity (
  machineKey TEXT PRIMARY KEY CHECK(length(machineKey)=32 AND machineKey NOT GLOB '*[^0-9a-f]*'),
  displayAlias TEXT NOT NULL CHECK(length(displayAlias) BETWEEN 1 AND 80),
  hostProfile TEXT NOT NULL CHECK(hostProfile IN ('androidSamsung','androidGeneric','linuxHost','windowsHost','macHost','synthetic')),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT,
  identityProven INTEGER CHECK(identityProven IN (0,1) OR identityProven IS NULL),
  isSynthetic INTEGER NOT NULL CHECK(isSynthetic IN (0,1)),
  CHECK(isSynthetic=1 OR identityProven IS NULL)
) STRICT;

CREATE TABLE deviceRecord (
  deviceKey TEXT PRIMARY KEY CHECK(length(deviceKey)=32 AND deviceKey NOT GLOB '*[^0-9a-f]*'),
  machineKey TEXT NOT NULL REFERENCES machineIdentity(machineKey) ON DELETE RESTRICT,
  category TEXT NOT NULL CHECK(category IN ('tablet','phone','desktop','raspberryPi','emulator','unknown')),
  modelAlias TEXT NOT NULL CHECK(length(modelAlias) BETWEEN 1 AND 80),
  verifiedBoot TEXT NOT NULL CHECK(verifiedBoot IN ('UNKNOWN','OBSERVED','REJECTED')),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT
) STRICT;
CREATE INDEX deviceByMachine ON deviceRecord(machineKey);

CREATE TABLE firmwareRecord (
  firmwareKey TEXT PRIMARY KEY CHECK(length(firmwareKey) BETWEEN 1 AND 80),
  deviceKey TEXT NOT NULL REFERENCES deviceRecord(deviceKey) ON DELETE RESTRICT,
  firmwareKind TEXT NOT NULL CHECK(firmwareKind IN ('bios','uefi','bootloader','osImage','kernel','vendor','unknown')),
  versionLabel TEXT NOT NULL CHECK(length(versionLabel) BETWEEN 1 AND 96),
  imageSha256 TEXT CHECK(imageSha256 IS NULL OR (length(imageSha256)=64 AND imageSha256 NOT GLOB '*[^0-9a-f]*')),
  verification TEXT NOT NULL CHECK(verification IN ('UNKNOWN','SOURCE_ONLY','HARDWARE_OBSERVED','REJECTED')),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT
) STRICT;
CREATE INDEX firmwareByDevice ON firmwareRecord(deviceKey);

CREATE TABLE namespaceRegistry (
  registryKey TEXT PRIMARY KEY CHECK(length(registryKey) BETWEEN 1 AND 80),
  namespaceKind TEXT NOT NULL CHECK(namespaceKind IN ('machine','package','api','dns','plugin','firmware')),
  normalizedName TEXT NOT NULL CHECK(length(normalizedName) BETWEEN 1 AND 255),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT,
  entryState TEXT NOT NULL CHECK(entryState IN ('SOURCE_ONLY','OBSERVED','UNKNOWN','REJECTED')),
  UNIQUE(namespaceKind,normalizedName,sourceRef)
) STRICT;

CREATE TABLE machineApi (
  apiKey TEXT PRIMARY KEY CHECK(length(apiKey) BETWEEN 1 AND 80),
  machineKey TEXT REFERENCES machineIdentity(machineKey) ON DELETE RESTRICT,
  method TEXT NOT NULL CHECK(method IN ('GET','HEAD','POST','MCP_TOOL','LOCAL')),
  surface TEXT NOT NULL CHECK(surface IN ('mcp','os','firmware','network','storage','build','ui')),
  routeLabel TEXT NOT NULL CHECK(length(routeLabel) BETWEEN 1 AND 240),
  accessPolicy TEXT NOT NULL CHECK(accessPolicy IN ('READ_ONLY','DENY','HUMAN_APPROVAL_REQUIRED')),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT
) STRICT;

CREATE TABLE artifactPointer (
  artifactKey TEXT PRIMARY KEY CHECK(length(artifactKey) BETWEEN 1 AND 80),
  sha256 TEXT NOT NULL CHECK(length(sha256)=64 AND sha256 NOT GLOB '*[^0-9a-f]*'),
  sizeBytes INTEGER NOT NULL CHECK(sizeBytes>=0),
  storageLane TEXT NOT NULL CHECK(storageLane IN ('githubSource','googleDriveDurable','ephemeralCi','localSynthetic')),
  logicalRef TEXT NOT NULL CHECK(length(logicalRef) BETWEEN 1 AND 500),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT,
  verification TEXT NOT NULL CHECK(verification IN ('UNKNOWN','SOURCE_ONLY','HASH_OBSERVED','REJECTED'))
) STRICT;
CREATE INDEX artifactByHash ON artifactPointer(sha256);

CREATE TABLE evidenceReceipt (
  receiptKey TEXT PRIMARY KEY CHECK(length(receiptKey) BETWEEN 1 AND 80),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT,
  evidenceDigest TEXT NOT NULL CHECK(length(evidenceDigest)=64 AND evidenceDigest NOT GLOB '*[^0-9a-f]*'),
  observedAt TEXT NOT NULL CHECK(length(observedAt) BETWEEN 20 AND 40 AND observedAt GLOB '????-??-??T??:??:??*Z'),
  evidenceKind TEXT NOT NULL CHECK(evidenceKind IN ('SOURCE_CI','DEVICE_LOCAL','NETWORK_LOCAL','FIRMWARE_LOCAL','MANUAL_REVIEW')),
  proofLevel TEXT NOT NULL CHECK(proofLevel IN ('UNKNOWN','SOURCE_ONLY','EXTERNALLY_VERIFIED','REJECTED')),
  -- The source-only audit never self-certifies external machine verification.
  CHECK(evidenceKind!='SOURCE_CI' OR proofLevel IN ('UNKNOWN','SOURCE_ONLY','REJECTED'))
) STRICT;

CREATE TABLE auditCoordinate (
  surface TEXT NOT NULL CHECK(surface IN
    ('identity','source','device','firmware','registry','machineApi','artifact','governance')),
  cellHex TEXT NOT NULL CHECK(length(cellHex)=4 AND substr(cellHex,1,2)='0x'
    AND substr(cellHex,3,1) GLOB '[0-3]' AND substr(cellHex,4,1) GLOB '[0-9A-F]'),
  castStage TEXT NOT NULL CHECK(castStage IN ('castTesting','castProposed','castBridge','cast')),
  interactionBeat TEXT NOT NULL CHECK(interactionBeat IN ('hear','resolve','act','verify')),
  auditTier TEXT NOT NULL CHECK(auditTier IN ('technologyFastPath','forFuckSake','scorchedEarth','finalForm')),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT,
  evaluation TEXT NOT NULL CHECK(evaluation IN ('PASS_SOURCE_ONLY','FAIL','HOLD')),
  PRIMARY KEY(surface,cellHex)
) STRICT;
CREATE INDEX auditByTier ON auditCoordinate(auditTier,interactionBeat,surface);


-- One stable operator-facing projection, NOT one denormalized source table.
CREATE VIEW machineStateOverview AS
SELECT m.machineKey, m.displayAlias, m.hostProfile, m.identityProven,
       d.deviceKey, d.category, d.verifiedBoot,
       f.firmwareKey, f.firmwareKind, f.versionLabel, f.imageSha256,
       m.sourceRef
FROM machineIdentity AS m
LEFT JOIN deviceRecord AS d ON d.machineKey=m.machineKey
LEFT JOIN firmwareRecord AS f ON f.deviceKey=d.deviceKey;

-- No secret, credential, physical IMEI/MAC/serial, raw firmware or media BLOB columns.
-- No SQL trigger may grant CAST, publish software, flash a device or modify source Canon.
