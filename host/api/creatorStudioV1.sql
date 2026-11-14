-- LuHm-OS creator studio. Additive local SQLite STRICT schema; no remote SQL port.
-- Existing host/api/typedLanesV1.sql remains the canonical event/typed-lane ledger.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS studioWorld(
 worldId TEXT PRIMARY KEY CHECK(length(worldId) BETWEEN 1 AND 80),
 product TEXT NOT NULL CHECK(product='LuHm-OS'),
 displayName TEXT NOT NULL CHECK(length(displayName) BETWEEN 1 AND 160),
 status TEXT NOT NULL CHECK(status IN ('draft','review','approvedSource')),
 sourceRef TEXT NOT NULL CHECK(length(sourceRef)=40 AND sourceRef NOT GLOB '*[^0-9a-f]*'),
 contentHash TEXT NOT NULL CHECK(length(contentHash)=64 AND contentHash NOT GLOB '*[^0-9a-f]*'),
 updatedAt TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS studioScene(
 worldId TEXT NOT NULL REFERENCES studioWorld(worldId) ON DELETE CASCADE,
 sceneId TEXT NOT NULL CHECK(length(sceneId) BETWEEN 1 AND 80),
 displayName TEXT NOT NULL CHECK(length(displayName) BETWEEN 1 AND 160),
 sceneKind TEXT NOT NULL CHECK(sceneKind IN ('socialHub','exploration','dungeon','cutscene')),
 paletteJson TEXT NOT NULL CHECK(json_valid(paletteJson)),
 spawnDialogueId TEXT NOT NULL, destinationId TEXT,
 PRIMARY KEY(worldId,sceneId)
) STRICT;
CREATE TABLE IF NOT EXISTS studioCharacter(
 worldId TEXT NOT NULL REFERENCES studioWorld(worldId) ON DELETE CASCADE,
 characterId TEXT NOT NULL, role TEXT NOT NULL,
 artState TEXT NOT NULL CHECK(artState IN ('proceduralPlaceholder','rightsReviewed','importVerified')),
 approvedRig INTEGER NOT NULL CHECK(approvedRig IN (0,1)),
 PRIMARY KEY(worldId,characterId)
) STRICT;
CREATE TABLE IF NOT EXISTS studioDialogue(
 worldId TEXT NOT NULL, lineId TEXT NOT NULL,sceneId TEXT NOT NULL,
 speakerId TEXT NOT NULL,intentTag TEXT NOT NULL CHECK(intentTag IN ('banter','bond','quest','route','combat','ambient','cutscene','system')),
 dialogueText TEXT NOT NULL CHECK(length(dialogueText) BETWEEN 1 AND 1000),
 choicesJson TEXT NOT NULL CHECK(json_valid(choicesJson)),
 PRIMARY KEY(worldId,lineId),
 FOREIGN KEY(worldId,sceneId) REFERENCES studioScene(worldId,sceneId),
 FOREIGN KEY(worldId,speakerId) REFERENCES studioCharacter(worldId,characterId)
) STRICT;
CREATE INDEX IF NOT EXISTS studioDialogueScene ON studioDialogue(worldId,sceneId,lineId);
CREATE TABLE IF NOT EXISTS studioMorphDraft(
 worldId TEXT NOT NULL,characterId TEXT NOT NULL,presetId TEXT NOT NULL,
 valuesJson TEXT NOT NULL CHECK(json_valid(valuesJson)),
 rigProof TEXT NOT NULL DEFAULT 'UNVERIFIED',
 publicAllowed INTEGER NOT NULL DEFAULT 0 CHECK(publicAllowed=0),
 PRIMARY KEY(worldId,characterId,presetId),
 FOREIGN KEY(worldId,characterId) REFERENCES studioCharacter(worldId,characterId)
) STRICT;
CREATE TABLE IF NOT EXISTS studioAiSuggestion(
 suggestionId TEXT PRIMARY KEY,worldId TEXT NOT NULL REFERENCES studioWorld(worldId),
 sourceRef TEXT NOT NULL CHECK(length(sourceRef)=40 AND sourceRef NOT GLOB '*[^0-9a-f]*'),
 proposer TEXT NOT NULL,proposalJson TEXT NOT NULL CHECK(json_valid(proposalJson)),
 reviewState TEXT NOT NULL DEFAULT 'proposed' CHECK(reviewState IN ('proposed','rejected','needsReview')),
 authorityGranted INTEGER NOT NULL DEFAULT 0 CHECK(authorityGranted=0)
) STRICT;
-- SQL stores references and text only. Image/GLB/animation masters remain in private asset storage.
