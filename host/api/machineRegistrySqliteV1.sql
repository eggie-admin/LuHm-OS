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

-- Additional machine catalogue categories are normalized facts, not raw hardware records.
-- No live collectors, executable commands, arbitrary EAV authority, or firmware binary content.
CREATE TABLE machineComponent (
  componentKey TEXT PRIMARY KEY CHECK(length(componentKey)=32 AND componentKey NOT GLOB '*[^0-9a-f]*'),
  machineKey TEXT REFERENCES machineIdentity(machineKey) ON DELETE RESTRICT,
  componentClass TEXT NOT NULL CHECK(componentClass IN
    ('cpu','gpu','memory','os','kernel','bios','uefi','bootloader','firmware','driver',
     'storage','filesystem','partition','network','dns','certificate','process','service',
     'package','library','plugin','api','model','runtime','container','vm','display','sensor','media')),
  displayName TEXT NOT NULL CHECK(length(displayName) BETWEEN 1 AND 120),
  versionLabel TEXT CHECK(versionLabel IS NULL OR length(versionLabel) BETWEEN 1 AND 96),
  contentSha256 TEXT CHECK(contentSha256 IS NULL OR (length(contentSha256)=64 AND contentSha256 NOT GLOB '*[^0-9a-f]*')),
  observation TEXT NOT NULL CHECK(observation IN ('UNKNOWN','SOURCE_ONLY','SYNTHETIC','DEVICE_LOCAL_REQUIRES_RECEIPT')),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT
) STRICT;
CREATE INDEX componentByClass ON machineComponent(componentClass,sourceRef);
CREATE TABLE machineComponentLink (
  componentKey TEXT NOT NULL REFERENCES machineComponent(componentKey) ON DELETE RESTRICT,
  relatedKey TEXT NOT NULL REFERENCES machineComponent(componentKey) ON DELETE RESTRICT,
  relationship TEXT NOT NULL CHECK(relationship IN ('dependsOn','contains','runsOn','exposes','compatibleWith')),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT,
  PRIMARY KEY(componentKey,relatedKey,relationship),
  CHECK(componentKey<>relatedKey)
) STRICT;

-- Opcode is a compact display/transport identifier, never an execution right.
-- 0xC1 is distinct from the reserved 0x00..0x3F audit-coordinate namespace.
CREATE TABLE castOpcodeRegistry (
  opcode TEXT PRIMARY KEY CHECK(opcode='0xC1'),
  asciiHex TEXT NOT NULL CHECK(asciiHex='43415354'),
  commandName TEXT NOT NULL CHECK(commandName='castIntent'),
  effect TEXT NOT NULL CHECK(effect='INTENT_ONLY'),
  grantsAuthority INTEGER NOT NULL DEFAULT 0 CHECK(grantsAuthority=0),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT
) STRICT;
CREATE TABLE aiManifestReceipt (
  manifestKey TEXT PRIMARY KEY CHECK(length(manifestKey)=32 AND manifestKey NOT GLOB '*[^0-9a-f]*'),
  opcode TEXT NOT NULL REFERENCES castOpcodeRegistry(opcode) ON DELETE RESTRICT,
  taskId TEXT NOT NULL CHECK(length(taskId) BETWEEN 1 AND 80),
  scopeId TEXT NOT NULL CHECK(length(scopeId) BETWEEN 1 AND 80),
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT,
  manifestSha256 TEXT NOT NULL UNIQUE CHECK(length(manifestSha256)=64 AND manifestSha256 NOT GLOB '*[^0-9a-f]*'),
  manifestJson TEXT NOT NULL CHECK(length(manifestJson) BETWEEN 2 AND 16384 AND json_valid(manifestJson)),
  effect TEXT NOT NULL CHECK(effect='INTENT_CANDIDATE_HOLD'),
  mutationGranted INTEGER NOT NULL DEFAULT 0 CHECK(mutationGranted=0),
  crownGranted INTEGER NOT NULL DEFAULT 0 CHECK(crownGranted=0),
  CHECK(json_extract(manifestJson,'$.schema')='luhmOs.aiTaskManifest.v2'),
  CHECK(json_extract(manifestJson,'$.machineBridge.opcode')='0xC1'),
  CHECK(json_extract(manifestJson,'$.machineBridge.displayName')='LuHm-OS'),
  CHECK(json_extract(manifestJson,'$.authority.mutation')=0),
  CHECK(json_extract(manifestJson,'$.authority.green')=0),
  CHECK(json_extract(manifestJson,'$.authority.crown')=0)
) STRICT;
CREATE INDEX manifestTaskScope ON aiManifestReceipt(taskId,scopeId,sourceRef);
CREATE TABLE castIntentReceipt (
  receiptKey TEXT PRIMARY KEY CHECK(length(receiptKey) BETWEEN 1 AND 80),
  manifestKey TEXT NOT NULL UNIQUE REFERENCES aiManifestReceipt(manifestKey) ON DELETE RESTRICT,
  sourceRef TEXT NOT NULL REFERENCES sourceRevision(sourceRef) ON DELETE RESTRICT,
  stage TEXT NOT NULL CHECK(stage='castBridge'),
  beat TEXT NOT NULL CHECK(beat IN ('hear','resolve','act','verify')),
  tier TEXT NOT NULL CHECK(tier IN ('technologyFastPath','forFuckSake','scorchedEarth','finalForm')),
  state TEXT NOT NULL CHECK(state='HOLD_SEPARATE_PROFESSOR_CAST'),
  dispatched INTEGER NOT NULL DEFAULT 0 CHECK(dispatched=0),
  authorityEffect TEXT NOT NULL CHECK(authorityEffect='none')
) STRICT;

-- No secret, credential, physical IMEI/MAC/serial, raw firmware or media BLOB columns.
-- No SQL trigger may grant CAST, publish software, flash a device or modify source Canon.
