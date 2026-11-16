# Canon hexadecimal evidence ledger (scoped source candidate)

This reuses tools/hydraHexReleaseAudit.py and the existing host/api/typedLanesV1.sql schema. It does not add a second database architecture, create a public SQL endpoint, activate agents, sign certificates, or turn 64 assessments into 64 passed tests.

## Commands

On a clean checked-out commit:

    python3 -m unittest -v tests.testCanonHexLedger
    python3 tools/canonHexLedger.py --db /tmp/luhm-canon-hex.db --report /tmp/luhm-canon-hex.json --all-scales --source-ref "$(git rev-parse HEAD)"

--slots 256 (default), --slots 512, --slots 1024, and --all-scales reuse existing HEX scale. Each 64 assessed slots yields a SHA-256 chained checkpoint with 0x000..0x03f per first window, and status counts. The 256/512/1024 matrices are independent; no evidence is promoted between scales. A source SHA change requires a new database and fresh receipts. Commit signature code from git log --format=%G? is metadata, not certificate-trust verification.

Only fields explicitly named for source SHA, digests, checksums or fingerprints are indexed from allowlisted doctrine/*.json. The scanner refuses secret, token, private-key, credential and PEM field names; raw PEM/certificate bodies and binary artifacts are not stored. Metadata values are valid lowercase hex strings of exactly 40 or 64 characters, with public source path and JSON pointer provenance. Unknown host certificate chain, leaf issuer and signing identity remain UNKNOWN. Certificate signing and key generation never occur.

SQLite uses the existing streamEvent, numericStream, textStream, booleanStream and aiManifestStream lanes. artifactPointer remains for independently verified file records. Every snapshot is created outside the source checkout with restricted permissions and atomic replace; no database is committed. V2 local proposal manifest has no mutation, GREEN or Crown authority. CI artifact storage is temporary, not a Google Drive durable archive.

## Licensing and 4×4 truth

Repository root currently states GPL version 3. Apache-2.0 components can generally coexist with GPLv3, but blanket relicensing requires rights/source and dependency review. Do not rewrite license files without that approval. Vendor removal is allowed only after functionality, licenses, entitlements and exact-source tests are preserved. machineSqlDragonTail → repositoryKebabNamespace → vowelRippedStrictCamelHump → fullHumanCenteredCamelHump is the existing Canon namespace ladder. API/vendor adapter is a subrole, not a fifth authority tier. operationTitan build 7, FFS (25), Scorched Earth (50) and Final Form structural audit are separate from 64-slot checkpoints.

## Stop groups

- GREEN_SOURCE: verified static source cells and exact CI metadata only.
- AMBER: actual TLS chain, authenticated private SQL persistence, runtime AI worker invocation, Android physical proof, vendor and licensing rights.
- HARD_RED: confirmed security, integrity, source identity, authority or certificate trust failure. Never auto-prune, override or promote.
- CROWN STOP: production signing/publication and Project Hydra closure remain human acceptance gates.

## Headless human-centered JavaScript adapter

The pure `frontEnd/core/canonHexLedger.mjs` reads sanitized HEX SQL report receipts, reuses existing Canon namespace names, groups GREEN/AMBER/RED/Crown counts, rejects stale source and broken checkpoint structure, and offers an eight-entry in-memory LRU keyed by exact source SHA and DB digest with explicit stale-source pruning. It does not access a vendor runtime, localStorage, remote SQL or keys. Without raw cells it cannot independently recalculate SHA256 chain contents; that remains the Python/CI verifier's job. This library is headless source, not an installed client or a new authority tier.
