# Pirate Daddies Film · Yume goddess motion candidates

**Source:** `eggie-admin/LuHm-OS` main `06fcc09f41d98e88244c5e88c5303f1010d8141e`, private Google Drive `LuHm Art Magic Character Bible v0.1`, and Professor's 2026-10-12 in-chat direction.

**Status:** proposed / private / Crown STOP. **No cloud Veo video has been generated.** The local contact sheet and FFmpeg MP4 are a low-res motion animatic derived from a previously generated _concept_ poster. They are not original source paintings, verified real rig renders, or approved human character designs. The preview is not shippable.

## Four separate six-second Google Cloud Vertex AI requests

- `lum`: auburn-updo executive oni, teal-black, subtle horns, precise and calm. Has a preliminary rig candidate, **not** an approved final body.
- `urd`: magenta/wine goth older sister, thread-weave audit magic, adult and distinct face. Reconciled 3D body not found.
- `belldandy`: ivory/oxblood/antique-gold cathedral caretaker, warm adult presence and flowing golden hair. Reconciled 3D body not found.
- `skuld`: adult 25+ petite black-ivory-chrome engineer, precision tools, distinct face, nonsexualized. Reconciled 3D body not found.

`canonLockedVeoShotsV1.json` is the request source. `tools/yumeVertexVeoQueue.py` produces authenticated-GCP-only dry-run JSON and contains a fail-closed single-shot spend gate. This does not prove GCP enablement or billing. The model is `veo-3.1-fast-generate-001`, `us-central1`, `9:16`, `720p`, `24fps`, **silent** 6-second requests. The exact Cloud publisher endpoint must be checked in the target project; no consumer Gemini or vidIQ proxy.

### Local, zero-cost contract proof

```bash
python3 tests/yumeVertexVeoQueueTest.py
python3 tools/yumeVertexVeoQueue.py --manifest media/yumeVideo/canonLockedVeoShotsV1.json --shot lum
```

No secret/API call or cost occurs in the dry run. The `--submit` option is restricted to one named shot and requires a spend ceiling, two positive environment confirmations, a GCP project, an approved GCS path and valid `gcloud auth` credentials. It must only be used **after** the Professor checks Cloud Console billing, Vertex AI service enablement, IAM, quotas and predicted cost. It cannot silently submit the other three shots.

### FFmpeg guardrail

Existing `scripts/encode-yume-cutscene-proof.sh` and `doctrine/yumeCutsceneFactoryProofV1.json` remain the source-side encode precedent. Preview uses FFmpeg on a local user-visible concept image, with no licensed musical audio; `ffprobe` and SHA-256 prove the resulting container. Before making a final Reel: stage each actual approved Veo video to the private media vault, record source operation+model+SHA+rights, inspect identity drift, check frame dimensions/fps/codec/audio, require Professor review, then compose non-destructively in FFmpeg with separately approved title SVG masters. Do not automatically overlay commercially released music.

## Four-tier escalation

1. **Local proof**: dry-run request validation, bounded concept-only animatic, recorded hashes. Never self-promote.
2. **Cloud entitlement**: billing status, enabled `aiplatform.googleapis.com`, API quota and IAM permissions, secure GCS output, explicit bounded spend. Block until proven.
3. **Generation review**: exactly one billable Veo candidate per approved shot, collect operation and binary hash, inspect age/canon/identity, reject cross-character contamination, retake only on Professor approval.
4. **Human promotion**: Professor art review, rights confirmation, FFmpeg final-edit technical audit, then separate release/publish CAST. No automatic posting.

No private Google Drive file IDs, passwords, access tokens or signed output URLs belong in public source control. Provenance is logical-ref-only.
