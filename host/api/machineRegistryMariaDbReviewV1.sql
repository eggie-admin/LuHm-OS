-- LuHm-OS / Project Premonition: MariaDB/phpMyAdmin REVIEW-ONLY schema.
-- DO NOT import into an actual database before owner approval, version pin,
-- backup/restore rehearsal, permission review and independent schema comparison.
-- Use InnoDB foreign keys, not phpMyAdmin's optional UI-only relations.
-- Designed for MariaDB 10.6+ review; compatibility has NOT been tested on server.
-- No CREATE DATABASE, GRANT, service startup, SQL port or stored secrets.
-- Full textual hex improves phpMyAdmin operator inspection at modest index cost.
-- Exact server-version CHECK behavior, collation and migration still require proof.

CREATE TABLE sourceRevision (
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
  treeDigest CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  upstream VARCHAR(80) NOT NULL,
  recordState ENUM('SOURCE_CANDIDATE','REVIEWED','UNKNOWN') NOT NULL,
  observedAt VARCHAR(40) NOT NULL,
  CONSTRAINT ckSourceRefHex CHECK(sourceRef REGEXP '^[0-9a-f]{40}$'),
  CONSTRAINT ckTreeDigestHex CHECK(treeDigest REGEXP '^[0-9a-f]{64}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE machineIdentity (
  machineKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
  displayAlias VARCHAR(80) NOT NULL,
  hostProfile ENUM('androidSamsung','androidGeneric','linuxHost','windowsHost','macHost','synthetic') NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  identityProven TINYINT NULL,
  isSynthetic TINYINT NOT NULL,
  CONSTRAINT fkMachineSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT ckMachineKeyHex CHECK(machineKey REGEXP '^[0-9a-f]{32}$'),
  CONSTRAINT ckMachinePrivacy CHECK(identityProven IS NULL OR identityProven IN (0,1)),
  CONSTRAINT ckMachineSynthetic CHECK(isSynthetic IN (0,1) AND (isSynthetic=1 OR identityProven IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE deviceRecord (
  deviceKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
  machineKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  category ENUM('tablet','phone','desktop','raspberryPi','emulator','unknown') NOT NULL,
  modelAlias VARCHAR(80) NOT NULL,
  verifiedBoot ENUM('UNKNOWN','OBSERVED','REJECTED') NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  CONSTRAINT fkDeviceMachine FOREIGN KEY(machineKey) REFERENCES machineIdentity(machineKey),
  CONSTRAINT fkDeviceSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  INDEX deviceByMachine(machineKey)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE firmwareRecord (
  firmwareKey VARCHAR(80) PRIMARY KEY,
  deviceKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  firmwareKind ENUM('bios','uefi','bootloader','osImage','kernel','vendor','unknown') NOT NULL,
  versionLabel VARCHAR(96) NOT NULL,
  imageSha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NULL,
  verification ENUM('UNKNOWN','SOURCE_ONLY','HARDWARE_OBSERVED','REJECTED') NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  CONSTRAINT fkFirmwareDevice FOREIGN KEY(deviceKey) REFERENCES deviceRecord(deviceKey),
  CONSTRAINT fkFirmwareSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT ckFirmwareDigest CHECK(imageSha256 IS NULL OR imageSha256 REGEXP '^[0-9a-f]{64}$'),
  INDEX firmwareByDevice(deviceKey)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE namespaceRegistry (
  registryKey VARCHAR(80) PRIMARY KEY,
  namespaceKind ENUM('machine','package','api','dns','plugin','firmware') NOT NULL,
  normalizedName VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  entryState ENUM('SOURCE_ONLY','OBSERVED','UNKNOWN','REJECTED') NOT NULL,
  CONSTRAINT fkRegistrySource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  UNIQUE KEY uniqueNamespaceSource(namespaceKind,normalizedName,sourceRef)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE machineApi (
  apiKey VARCHAR(80) PRIMARY KEY,
  machineKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NULL,
  method ENUM('GET','HEAD','POST','MCP_TOOL','LOCAL') NOT NULL,
  surface ENUM('mcp','os','firmware','network','storage','build','ui') NOT NULL,
  routeLabel VARCHAR(240) NOT NULL,
  accessPolicy ENUM('READ_ONLY','DENY','HUMAN_APPROVAL_REQUIRED') NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  CONSTRAINT fkApiMachine FOREIGN KEY(machineKey) REFERENCES machineIdentity(machineKey),
  CONSTRAINT fkApiSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE artifactPointer (
  artifactKey VARCHAR(80) PRIMARY KEY,
  sha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  sizeBytes BIGINT NOT NULL,
  storageLane ENUM('githubSource','googleDriveDurable','ephemeralCi','localSynthetic') NOT NULL,
  logicalRef VARCHAR(500) NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  verification ENUM('UNKNOWN','SOURCE_ONLY','HASH_OBSERVED','REJECTED') NOT NULL,
  CONSTRAINT fkArtifactSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT ckArtifactSha CHECK(sha256 REGEXP '^[0-9a-f]{64}$'),
  CONSTRAINT ckArtifactSize CHECK(sizeBytes>=0),
  INDEX artifactByHash(sha256)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE evidenceReceipt (
  receiptKey VARCHAR(80) PRIMARY KEY,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  evidenceDigest CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  observedAt VARCHAR(40) NOT NULL,
  evidenceKind ENUM('SOURCE_CI','DEVICE_LOCAL','NETWORK_LOCAL','FIRMWARE_LOCAL','MANUAL_REVIEW') NOT NULL,
  proofLevel ENUM('UNKNOWN','SOURCE_ONLY','EXTERNALLY_VERIFIED','REJECTED') NOT NULL,
  CONSTRAINT fkReceiptSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT ckReceiptDigest CHECK(evidenceDigest REGEXP '^[0-9a-f]{64}$'),
  CONSTRAINT ckNoSelfCertifiedExternal CHECK(evidenceKind!='SOURCE_CI' OR proofLevel!='EXTERNALLY_VERIFIED')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE auditCoordinate (
  surface ENUM('identity','source','device','firmware','registry','machineApi','artifact','governance') NOT NULL,
  cellHex CHAR(4) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  castStage ENUM('castTesting','castProposed','castBridge','cast') NOT NULL,
  interactionBeat ENUM('hear','resolve','act','verify') NOT NULL,
  auditTier ENUM('technologyFastPath','forFuckSake','scorchedEarth','finalForm') NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  evaluation ENUM('PASS_SOURCE_ONLY','FAIL','HOLD') NOT NULL,
  PRIMARY KEY(surface,cellHex),
  CONSTRAINT fkAuditSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT ckAuditHex CHECK(cellHex REGEXP '^0x[0-3][0-9A-F]$'),
  INDEX auditByTier(auditTier,interactionBeat,surface)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Read-only SQL SELECT convenience in phpMyAdmin's Views/SQL tabs.
-- Requires the same reviewed permissions as the underlying tables.
CREATE VIEW machineStateOverview AS
SELECT m.machineKey, m.displayAlias, m.hostProfile, m.identityProven,
       d.deviceKey, d.category, d.verifiedBoot,
       f.firmwareKey, f.firmwareKind, f.versionLabel, f.imageSha256,
       m.sourceRef
FROM machineIdentity AS m
LEFT JOIN deviceRecord AS d ON d.machineKey=m.machineKey
LEFT JOIN firmwareRecord AS f ON f.deviceKey=d.deviceKey;

-- REVIEW ONLY: compile/test exact MariaDB version and check_constraint_checks=ON
-- before any staged migration. PHP/phpMyAdmin is not required by the Python bridge.
CREATE TABLE machineComponent (
  componentKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
  machineKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NULL,
  componentClass ENUM('cpu','gpu','memory','os','kernel','bios','uefi','bootloader',
    'firmware','driver','storage','filesystem','partition','network','dns','certificate',
    'process','service','package','library','plugin','api','model','runtime',
    'container','vm','display','sensor','media') NOT NULL,
  displayName VARCHAR(120) NOT NULL,
  versionLabel VARCHAR(96),
  contentSha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin,
  observation ENUM('UNKNOWN','SOURCE_ONLY','SYNTHETIC','DEVICE_LOCAL_REQUIRES_RECEIPT') NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  CONSTRAINT fkComponentMachine FOREIGN KEY(machineKey) REFERENCES machineIdentity(machineKey),
  CONSTRAINT fkComponentSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT ckComponentKeyHex CHECK(componentKey REGEXP '^[0-9a-f]{32}
-- InnoDB constraints. Its separate pmadb tables are optional UI metadata,
-- never LuHm machine source or permission authority. No public admin route.
),
  CONSTRAINT ckComponentDigest CHECK(contentSha256 IS NULL OR contentSha256 REGEXP '^[0-9a-f]{64}
-- InnoDB constraints. Its separate pmadb tables are optional UI metadata,
-- never LuHm machine source or permission authority. No public admin route.
),
  INDEX componentByClass(componentClass,sourceRef)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE machineComponentLink (
  componentKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  relatedKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  relationship ENUM('dependsOn','contains','runsOn','exposes','compatibleWith') NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  PRIMARY KEY(componentKey,relatedKey,relationship),
  CONSTRAINT fkLinkSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT fkLinkFrom FOREIGN KEY(componentKey) REFERENCES machineComponent(componentKey),
  CONSTRAINT fkLinkTo FOREIGN KEY(relatedKey) REFERENCES machineComponent(componentKey),
  CONSTRAINT ckNoSelfLink CHECK(componentKey<>relatedKey)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE castOpcodeRegistry (
  opcode CHAR(4) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
  asciiHex CHAR(8) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  commandName VARCHAR(40) NOT NULL,
  effect ENUM('INTENT_ONLY') NOT NULL,
  grantsAuthority TINYINT NOT NULL DEFAULT 0,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  CONSTRAINT ckCastOpcode CHECK(opcode='0xC1' AND asciiHex='43415354'
    AND commandName='castIntent' AND grantsAuthority=0),
  CONSTRAINT fkCastOpcodeSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE aiManifestReceipt (
  manifestKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
  opcode CHAR(4) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  taskId VARCHAR(80) NOT NULL,
  scopeId VARCHAR(80) NOT NULL,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  manifestSha256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL UNIQUE,
  manifestJson LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  effect ENUM('INTENT_CANDIDATE_HOLD') NOT NULL,
  mutationGranted TINYINT NOT NULL DEFAULT 0,
  crownGranted TINYINT NOT NULL DEFAULT 0,
  CONSTRAINT fkManifestOpcode FOREIGN KEY(opcode) REFERENCES castOpcodeRegistry(opcode),
  CONSTRAINT fkManifestSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT ckManifestHex CHECK(manifestKey REGEXP '^[0-9a-f]{32}
-- InnoDB constraints. Its separate pmadb tables are optional UI metadata,
-- never LuHm machine source or permission authority. No public admin route.

    AND manifestSha256 REGEXP '^[0-9a-f]{64}
-- InnoDB constraints. Its separate pmadb tables are optional UI metadata,
-- never LuHm machine source or permission authority. No public admin route.
),
  CONSTRAINT ckManifestJsonValid CHECK(JSON_VALID(manifestJson)=1 AND CHAR_LENGTH(manifestJson)<=16384),
  CONSTRAINT ckManifestNoGrant CHECK(mutationGranted=0 AND crownGranted=0),
  CONSTRAINT ckManifestOpcodeInJson CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.machineBridge.opcode')),'')='0xC1'),
  CONSTRAINT ckManifestBrand CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.machineBridge.displayName')),'')='LuHm-OS'),
  CONSTRAINT ckManifestSameSource CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.sourceRef')),'')=sourceRef),
  CONSTRAINT ckManifestSameTask CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.taskId')),'')=taskId),
  CONSTRAINT ckManifestSameScope CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.scopeId')),'')=scopeId),
  CONSTRAINT ckManifestStage CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.machineBridge.stage')),'')='castBridge'),
  CONSTRAINT ckManifestNoSelfGrant CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.authority.mutation')),'')='false'
    AND COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.authority.green')),'')='false'
    AND COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.authority.crown')),'')='false'),
  CONSTRAINT ckManifestNoDispatch CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.machineBridge.dispatchAuthorized')),'')='false'
    AND COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.machineBridge.machineSqlWritable')),'')='false'),
  CONSTRAINT ckManifestBudget CHECK(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.budget.maxRequests')),'')='1'
    AND COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.budget.maxParallel')),'')='1'
    AND COALESCE(JSON_UNQUOTE(JSON_EXTRACT(manifestJson,'$.budget.maxPasses')),'')='1'),
  INDEX manifestTaskScope(taskId,scopeId,sourceRef)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE castIntentReceipt (
  receiptKey VARCHAR(80) PRIMARY KEY,
  manifestKey CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL UNIQUE,
  sourceRef CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  stage ENUM('castBridge') NOT NULL,
  beat ENUM('hear','resolve','act','verify') NOT NULL,
  tier ENUM('technologyFastPath','forFuckSake','scorchedEarth','finalForm') NOT NULL,
  state ENUM('HOLD_SEPARATE_PROFESSOR_CAST') NOT NULL,
  dispatched TINYINT NOT NULL DEFAULT 0,
  authorityEffect ENUM('none') NOT NULL,
  CONSTRAINT fkIntentManifest FOREIGN KEY(manifestKey) REFERENCES aiManifestReceipt(manifestKey),
  CONSTRAINT fkIntentSource FOREIGN KEY(sourceRef) REFERENCES sourceRevision(sourceRef),
  CONSTRAINT ckIntentNoDispatch CHECK(dispatched=0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- phpMyAdmin may display foreign-key links/Designer because these are real
-- InnoDB constraints. Its separate pmadb tables are optional UI metadata,
-- never LuHm machine source or permission authority. No public admin route.
