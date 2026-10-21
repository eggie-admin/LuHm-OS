# Yume / Goddess cabinet: private art hardening

**Source tool:** `tools/artAssetIntegrity.py`. Python 3 standard library only. Execute locally after retrieving owner-authorized files. Do not run on unreviewed archives as an exporter or animator.

**Lum** coordinates, **Yume** classifies design/mesh/rig readiness, **Urd** audits byte identity and invalid archive structures, **Belldandy** reconciles hash-pinned receipts, and **Skuld** separates copyright/provenance from technical integrity. These are **supervised conversational review roles**, not 15 active backend task workers.

## Safe workflow

1. Use the existing owner-only `LuHmOS_Rebel_PrivateProduction_20261020` Drive folder. Original EVE source sharing remains a separate unresolved risk; inspect only the owner-restricted working copy.
2. Run `python3 tools/artAssetIntegrity.py --self-test` first. No network, unarchiving, file writes outside optional JSON receipt, or code execution from donor files.
3. Inspect a private ZIP with `python3 tools/artAssetIntegrity.py --archive /private/asset.zip --output /private/report.json --source-ref COMMIT_SHA`.
4. For the private starter ZIP, also pass `--catalog /private/assetCatalog.json`. The tool checks all registered SHA-256 values, size mismatches, missing/unexpected members, path traversal, symbolic links, encryption, case-insensitive path collisions, uncompressed size, and suspicious compression ratios.
5. Inspect locally held sources using repeated `--file /private/model.glb` or `--file /private/source.blend` flags. GLB metadata and Blender version headers **do not establish** character rig quality, texture completeness, rights, canon or a Godot import proof.
6. Save JSON reports privately. Only source code and non-sensitive test fixtures belong in GitHub. Do not commit donor archives, extracted meshes, model/video masters, identifying Drive URLs, signers or secrets.

## Publication checklist

**Tech:** Blender scene opens; packed/external texture review; humanoid bone/weight normalization; pose stress; Godot 4.7 GLB import; UI and mobile memory/frame-rate proof. **Rights:** asset creator, license, derivative permission and public-redistribution authority. **Canon:** Yume identity pass, Urd proof, Professor visual approval. An asset passing ZIP/hash verification is still **not approved for publication**.

For Kenney packs, the archive declares CC0; keep font files private by default and review SVG source before embedding. Promote only a curated set of approved final PNGs or sanitized vector derivatives. For third-party EVE and the bar-scene donor, preserve rights-pending private state.

**Release boundary:** no asset promotion, no new agent permissions, and no release-signing effect from this tool. If receipts conflict, quarantine the candidate.
