-- Apply only to Professor-approved EXISTING SQL database using a least-privilege admin.
-- Verify backup/snapshot first. No production worker performs DDL.
-- Portable column definitions for PostgreSQL and MySQL 8 / MariaDB; test in staging first.
CREATE TABLE IF NOT EXISTS yumeVideoJob (
    taskId VARCHAR(80) PRIMARY KEY,
    sourceRef CHAR(40) NOT NULL,
    shotId VARCHAR(20) NOT NULL,
    requestHash CHAR(64) NOT NULL,
    state VARCHAR(40) NOT NULL,
    operationName VARCHAR(320),
    resultUri VARCHAR(1500),
    createdAt VARCHAR(40) NOT NULL,
    updatedAt VARCHAR(40) NOT NULL,
    attemptCount INTEGER NOT NULL DEFAULT 0,
    failureCode VARCHAR(80)
);
