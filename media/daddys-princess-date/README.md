# Daddy's Princess Gets Her Date

Private-media / public-edit-code lane for a short-form Pirate Daddies Film.

## Master target

- title: `Daddy's Princess Gets Her Date`
- runtime target: **02:30** (inside the requested ~3 minute Facebook post envelope)
- master: **1080x1920 / 9:16 / 30 fps / H.264 + AAC**
- brand: **PIRATE DADDIES FILM**
- end subtitle: **Remember... All Daddies Love You**
- pacing: fast hook, micro-cuts early, deliberate breathing room in the emotional middle, pattern interrupt every ~8-12 seconds
- captions: burned-in or sidecar, designed to work with sound off

## Privacy / authorship boundary

Raw photos, voice, video, and the current Kristin Lum / Big Daddy reference sheet stay **outside this public repository**. GitHub stores edit logic, manifests, prompts, validation, and receipts only.

Google AI Edge Gallery is the local planning assistant:
1. Ask Image -> continuity/canon notes from the local reference sheet.
2. Prompt Lab -> beat cards, alt captions, shot ideas.
3. Audio Scribe -> scratch voiceover transcription.
4. AI Chat -> continuity pass against the manifest.

Edge Gallery does not have to be the video renderer. The deterministic renderer is FFmpeg.

## Local render

```bash
bash scripts/render-daddys-princess-date.sh \
  /path/to/private/source-clips \
  /path/to/output/daddys-princess-date.mp4
```

Expected local clips are numbered in edit order, for example:

```text
01-hook.mp4
02-ready.mp4
03-outfit.mp4
04-dad-clock.mp4
...
```

The script normalizes the clips, concatenates them, then adds the Pirate Daddies Film end card.

## No automatic publication

This lane creates a candidate edit only. It does not publish to Facebook, merge to main, or grant any release/Crown authority.
