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

-- phpMyAdmin may display foreign-key links/Designer because these are real
-- InnoDB constraints. Its separate pmadb tables are optional UI metadata,
-- never LuHm machine source or permission authority. No public admin route.
