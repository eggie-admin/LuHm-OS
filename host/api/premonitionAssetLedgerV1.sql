-- LuHm-OS Project Premonition source-only asset metadata schema.
-- SQLite STRICT. This is executed IN MEMORY by the offline auditor only.
-- Raw SVG, Blender, GLB, media bytes and user secrets must not be stored here.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS premonitionAssetRecord(
  assetId TEXT PRIMARY KEY CHECK(length(assetId) BETWEEN 1 AND 80),
  taskId TEXT NOT NULL CHECK(length(taskId) BETWEEN 1 AND 80),
  sourceRef TEXT NOT NULL CHECK(length(sourceRef)=40 AND sourceRef NOT GLOB '*[^0-9a-f]*'),
  scopeId TEXT NOT NULL CHECK(length(scopeId) BETWEEN 1 AND 80),
  assetClass TEXT NOT NULL CHECK(assetClass IN ('vectorBrand','threeD','dataProcessing')),
  format TEXT NOT NULL CHECK(format IN ('svg','blend','glb','gltf','png','webp','mp4','wav')),
  sha256Hex TEXT NOT NULL CHECK(length(sha256Hex)=64 AND sha256Hex NOT GLOB '*[^0-9a-f]*'),
  byteCount INTEGER NOT NULL CHECK(byteCount >= 0 AND byteCount <= 1073741824),
  logicalPrivatePointer TEXT NOT NULL CHECK(length(logicalPrivatePointer) BETWEEN 1 AND 160),
  rightsState TEXT NOT NULL CHECK(rightsState IN ('PRIVATE_REVIEW','RIGHTS_CLEARED')),
  provenanceState TEXT NOT NULL CHECK(provenanceState IN ('UNKNOWN','SELF_AUTHORED','REVIEWED_EXTERNAL')),
  publicReleaseAuthorized INTEGER NOT NULL DEFAULT 0 CHECK(publicReleaseAuthorized=0),
  UNIQUE(taskId,sourceRef,scopeId,sha256Hex,assetClass)
) STRICT;
CREATE INDEX IF NOT EXISTS premonitionAssetTaskSource ON
  premonitionAssetRecord(taskId,sourceRef,scopeId,assetClass,assetId);
CREATE TABLE IF NOT EXISTS premonitionTransformRecord(
  eventId TEXT PRIMARY KEY CHECK(length(eventId) BETWEEN 1 AND 80),
  assetId TEXT NOT NULL REFERENCES premonitionAssetRecord(assetId),
  transformName TEXT NOT NULL CHECK(transformName IN ('inspect','thumbnailPlan','gltfValidationPlan','svgSanitizePlan')),
  executionState TEXT NOT NULL CHECK(executionState IN ('PLANNED_ONLY','HOLD')),
  inputSha256Hex TEXT NOT NULL CHECK(length(inputSha256Hex)=64),
  outputSha256Hex TEXT CHECK(outputSha256Hex IS NULL),
  ownerApproval INTEGER NOT NULL DEFAULT 0 CHECK(ownerApproval=0)
) STRICT;
CREATE INDEX IF NOT EXISTS premonitionTransformByAsset ON
  premonitionTransformRecord(assetId,transformName);
