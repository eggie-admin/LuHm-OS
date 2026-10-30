-- In-memory SQL receipt only. This is not production DB migration.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sourceReceipt(
 id TEXT PRIMARY KEY CHECK(length(id) BETWEEN 1 AND 64),
 sourceRef TEXT NOT NULL CHECK(length(sourceRef)=40 AND sourceRef NOT GLOB '*[^0-9a-f]*'),
 scopeId TEXT NOT NULL CHECK(length(scopeId) BETWEEN 1 AND 64),
 canonical TEXT NOT NULL CHECK(json_valid(canonical) AND json_extract(canonical,'$.sourceRef')=sourceRef AND json_extract(canonical,'$.scopeId')=scopeId AND json_extract(canonical,'$.approval')=0 AND json_extract(canonical,'$.costUsd')=0 AND json_extract(canonical,'$.crown')='STOP'),
 costCents INTEGER NOT NULL DEFAULT 0 CHECK(costCents=0),
 approval INTEGER NOT NULL DEFAULT 0 CHECK(approval=0),
 execution INTEGER NOT NULL DEFAULT 0 CHECK(execution=0),
 released INTEGER NOT NULL DEFAULT 0 CHECK(released=0)
) STRICT;
CREATE INDEX IF NOT EXISTS sourceReceiptRef ON sourceReceipt(sourceRef,scopeId);
