-- Candidate only. Do not apply to production or expose MariaDB ports.
-- Compatible with an operator-provisioned private MariaDB database.
-- SHA digests and refs are binary-collated ASCII hex strings, not encrypted data.
CREATE TABLE IF NOT EXISTS luhm_update_receipt (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(80) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    source_ref CHAR(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    scope_id VARCHAR(80) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    artifact_id VARCHAR(80) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    sha256_hex CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    local_state ENUM('HOLD','STOP','HOLD_FOR_PROFESSOR') NOT NULL,
    stage_count TINYINT UNSIGNED NOT NULL,
    observed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_stage_count CHECK (stage_count BETWEEN 1 AND 4),
    CONSTRAINT chk_sha256_length CHECK (CHAR_LENGTH(sha256_hex) = 64),
    CONSTRAINT chk_source_length CHECK (CHAR_LENGTH(source_ref) = 40),
    UNIQUE KEY exact_receipt (task_id,source_ref,scope_id,artifact_id,sha256_hex),
    KEY by_source (source_ref,scope_id,observed_at)
) ENGINE=InnoDB;
