# LuHm Storage Law v1

Canonical machine identity: `storageLaw`

## Prime law

`databases point to files; databases do not become the file server`

This is a role model, not a claim that OpenAI or GitHub literally run MariaDB for LuHm.

## Topology

- OpenAI = `semanticDb`: conversation context, agent state, decisions, semantic indexing, and references. It is not canonical source and never stores canonical project binaries.
- GitHub = `sourceDb`: source code, commits, branches, PRs, CI receipts, hashes, and pointers. GitHub Releases and CI artifacts are transport/cache only, not durable archive authority.
- Google Drive = `fileServer`: durable APKs, ZIPs, media, snapshots, manuals, recovery bundles, exports, and other large project binaries.
- Android/Termux = `runtimeMount`: installed runtime, bounded cache, and physical proof. Device presence is not source authority.

## Artifact law

Every durable binary must have a Drive-backed artifact record containing at least filename, SHA-256, exact sourceRef, build run, logical Drive reference, MIME type, size, and status.

A GitHub receipt points to the Drive file. It does not replace it.

The normal lifecycle is:

`buildEphemeral -> hashVerify -> driveDurableCopy -> githubPointerReceipt -> transportIfNeeded -> garbageCollectEphemeral`

## Authority

Storage location does not grant GREEN, publication authority, signing authority, or Crown. Professor remains final authority. Unknown storage identity remains UNKNOWN.
