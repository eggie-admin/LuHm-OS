-- LuHm-OS studio index: SQLite 3 review/development schema (no secrets, no binary blobs).
-- Source authority is GitHub; database stores metadata, pointers and receipts only.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS brand (
 brand_id TEXT PRIMARY KEY CHECK(length(brand_id) BETWEEN 1 AND 80),
 display_name TEXT NOT NULL,
 brand_role TEXT NOT NULL,
 claimed_legal_registration INTEGER NOT NULL DEFAULT 0 CHECK(claimed_legal_registration IN (0,1)),
 source_commit TEXT NOT NULL CHECK(length(source_commit)=40)
);
CREATE TABLE IF NOT EXISTS release_lane (
 lane_id TEXT PRIMARY KEY,
 visibility TEXT NOT NULL CHECK(visibility IN ('private','inviteOnly','public')),
 public_asset_eligible INTEGER NOT NULL CHECK(public_asset_eligible IN (0,1)),
 owner_approval_required INTEGER NOT NULL DEFAULT 1 CHECK(owner_approval_required=1),
 note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS social_account (
 platform TEXT NOT NULL,
 account_handle TEXT NOT NULL,
 publisher_brand_id TEXT NOT NULL REFERENCES brand(brand_id),
 connected_provider TEXT NOT NULL,
 posting_verified INTEGER NOT NULL CHECK(posting_verified IN (0,1)),
 PRIMARY KEY(platform,account_handle)
);
CREATE TABLE IF NOT EXISTS social_release (
 platform TEXT NOT NULL,
 provider_media_id TEXT NOT NULL,
 brand_id TEXT NOT NULL REFERENCES brand(brand_id),
 public_permalink TEXT NOT NULL CHECK(public_permalink LIKE 'https://%'),
 source_commit TEXT NOT NULL CHECK(length(source_commit)=40),
 provider_receipt TEXT NOT NULL,
 verified_at_utc TEXT NOT NULL,
 PRIMARY KEY(platform,provider_media_id)
);
CREATE TABLE IF NOT EXISTS artifact_pointer (
 artifact_id TEXT PRIMARY KEY,
 brand_id TEXT NOT NULL REFERENCES brand(brand_id),
 git_path TEXT,
 sha256 TEXT CHECK(sha256 IS NULL OR (length(sha256)=64 AND sha256 NOT GLOB '*[^0-9a-f]*')),
 visibility TEXT NOT NULL CHECK(visibility IN ('private','inviteOnly','public')),
 rights_status TEXT NOT NULL CHECK(rights_status IN ('pending','cleared')),
 owner_approval_status TEXT NOT NULL CHECK(owner_approval_status IN ('pending','approved')),
 release_lane_id TEXT NOT NULL REFERENCES release_lane(lane_id),
 CHECK(visibility!='public' OR (rights_status='cleared' AND owner_approval_status='approved'))
);
CREATE TABLE IF NOT EXISTS provider_route (
 provider_id TEXT PRIMARY KEY,
 provider_type TEXT NOT NULL,
 evidence_state TEXT NOT NULL CHECK(evidence_state IN ('verified','unverified','disabled')),
 credential_location TEXT NOT NULL CHECK(credential_location NOT IN ('database','github','chat')),
 billing_authorized INTEGER NOT NULL DEFAULT 0 CHECK(billing_authorized IN (0,1)),
 task_priority INTEGER NOT NULL,
 notes TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS signing_enrollment (
 vendor TEXT PRIMARY KEY,
 trust_purpose TEXT NOT NULL,
 enrollment_state TEXT NOT NULL CHECK(enrollment_state IN ('unverified','verified','disabled')),
 public_fingerprint TEXT CHECK(public_fingerprint IS NULL OR (length(public_fingerprint)>=32 AND public_fingerprint NOT GLOB '*[^a-fA-F0-9:]*')),
 key_material_location TEXT NOT NULL CHECK(key_material_location IN ('ownerHsm','ownerSecureEnclave','ownerEncryptedVault','providerManaged','notProvisioned')),
 verified_at_utc TEXT,
 proof_ref TEXT,
 CHECK(enrollment_state!='verified' OR (public_fingerprint IS NOT NULL AND proof_ref IS NOT NULL))
);
CREATE TABLE IF NOT EXISTS firmware_release (
 release_id TEXT PRIMARY KEY,
 artifact_sha256 TEXT CHECK(artifact_sha256 IS NULL OR length(artifact_sha256)=64),
 source_commit TEXT NOT NULL CHECK(length(source_commit)=40),
 lane_id TEXT NOT NULL REFERENCES release_lane(lane_id),
 platform TEXT NOT NULL,
 update_signer TEXT REFERENCES signing_enrollment(vendor),
 hardware_test_proof TEXT,
 rollback_proof TEXT,
 publication_state TEXT NOT NULL CHECK(publication_state IN ('candidate','blocked','published')),
 CHECK(publication_state!='published' OR (artifact_sha256 IS NOT NULL AND update_signer IS NOT NULL AND hardware_test_proof IS NOT NULL AND rollback_proof IS NOT NULL))
);
CREATE TABLE IF NOT EXISTS task_receipt (
 receipt_id TEXT PRIMARY KEY,
 source_commit TEXT NOT NULL CHECK(length(source_commit)=40),
 task_id TEXT NOT NULL,
 provider_id TEXT REFERENCES provider_route(provider_id),
 task_state TEXT NOT NULL CHECK(task_state IN ('proposed','blocked','verified','failed')),
 authority TEXT NOT NULL,
 evidence_ref TEXT,
 created_at_utc TEXT NOT NULL,
 CHECK(task_state!='verified' OR evidence_ref IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS idx_social_release_brand ON social_release(brand_id,verified_at_utc);
CREATE INDEX IF NOT EXISTS idx_artifact_visibility ON artifact_pointer(visibility,release_lane_id);
CREATE INDEX IF NOT EXISTS idx_task_source ON task_receipt(source_commit,task_id);
