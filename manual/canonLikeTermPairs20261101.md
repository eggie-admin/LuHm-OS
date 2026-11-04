# CAST | 2×2 like-term Canon reconciliation | 2026-11-01

**Status: PROPOSED SOURCE ONLY.** The index is a review map, not a replacement source of truth, an asset migration, a semantic auto-merge engine, or a release approval.

## Existing authority, never duplicated

- Source identity: `doctrine/currentSourceTruthV3.json`.
- Conversation/project naming: `doctrine/projectChatCanonV1.json` and internal-only `doctrine/workingTitleCastV1.json`.
- Machine naming: `doctrine/namingNamespaceCanonV1.json`; specialized `doctrine/camelHumpDoctrineLawV1.json`, `doctrine/currentFormatLawV1.json` and `doctrine/aiManifestFormatV1.json`.
- Operations: `doctrine/chatLikeTermFoldV1.json` and `tools/chatLikeTermFold.py`. These group like operations, **not** arbitrary file names.
- Word and role meaning: `doctrine/termResolutionV1.json`; metaphors `doctrine/semanticDomainHardeningV1.json`.
- Four-layer composition: `doctrine/luHmOSFourLayerArchitectureV1.json`. Older jQuery architecture is historical compatibility only.
- Evidence and rights: `doctrine/storageTopologyV1.json`, `doctrine/typedFourLaneSqlV1.json`, `game/canon/CHARACTER_CANON_V1.json` and `game/assets/ASSET_MANIFEST_V1.json`.
- Promotion boundary: `doctrine/everlastingCovenantV1.json`, `doctrine/proposedWorkingLaneV1.json`, `doctrine/releaseBoundaryV2.json`.

## Pairwise four passes

| Pair | Left | Right | Verdict |
| --- | --- | --- | --- |
| 0 / Identity | canonical human/machine identity | alias, display title or historical spelling | resolve explicitly or UNKNOWN |
| 1 / Contract | schema, law or doctrine | adapter, implementation or manifest example | relate without transferring authority |
| 2 / Evidence | source/CI candidate | live host/device, runtime/rights proof | do **not** infer proof from source |
| 3 / Lifecycle | current scoped authority | older snapshot or superseded item | preserve original, point to successor |

`doctrine/canonLikeTermPairsV1.json` seeds 20 reviewed-relationship *candidates* across source identity, naming, composition, workflow, schema, storage, platform, studio and release. Its `anchorPath` is the reference for that specific comparison, not permission to globally supersede everything with a similar title.

Only explicit relations are allowed: `supersedes`, `aliasOnly`, `specializes`, `differentAxes`, `implements`, `complements`. `supersedes` must be corroborated by an existing explicit pointer in the newer source. A tool must never infer supersession from matching basename, uppercase/lowercase spelling, SHA prefix, or a shared word.

### First examples

- **Current truth / September truth**: current-source document points to historical `SOURCE_OF_TRUTH.json`; no rewriting historical receipts.
- **Four-layer LuHmOS / jQuery four-layer**: source establishes the package naming successor; no forced source moves.
- **Term resolution / operation batching**: both operate on “like terms,” but one resolves names and the other batches duplicate work. They are **different axes**.
- **Typed SQL / storage topology**: numeric/text/Boolean/AI stream types describe events; Google Drive/source/file-server roles describe persistence. They are **different axes**.
- **Character Canon / asset slots**: design identity does not prove an approved GLB, rights or live import.
- **Current release boundary / September release boundary**: current doctrine references the legacy source, but still forbids unauthorized release.

## Climb only when an exception remains

1. **2×2:** compare only two verified paths, assess all four distinctions. Avoid a global rewrite.
2. **4×4:** group adjacent approved pairs by domain, then compare the common naming/authority/evidence/format boundaries.
3. **8×8:** expand only conflicting or missing-path domains, preserving exact `sourceRef` and provenance.
4. **16×16:** reserve for genuinely cross-domain conflicts that narrower deterministic scans cannot resolve; no automatic megamerge.

## Read-only run

```bash
python3 tools/canonLikeTermPairsAudit.py --output build/canon-like-terms/receipt.json
python3 -m unittest tests/test_canon_like_term_pairs.py -v
```

The audit inventories all top-level `doctrine/*.json` for declared schema IDs, source-status strings, non-unique schemas, unparseable files, and missing schema declarations. These are **review leads**, not automatic evidence that any doctrine file is broken. The output remains capped and avoids transferring any private Drive contents.

Accept only exact-source CI and a reviewed diff. No auto delete, rename, copy, schema mutation, Cloudflare edit, plugin enablement, Samsung install, asset release or Crown. New `sourceRef` always restarts verification.
