# Professor's Garage

Professor's Garage is the Tier 0 private workshop for LuHm OS experiments, media surgery, Godot/Blender work, and reproducible source mutation.

## Boot

Create or rebuild a GitHub Codespace from this branch. The devcontainer runs:

```bash
bash tools/professorGarageBootstrap.sh
```

Runtime truth is reported by:

```bash
python3 tools/professorGarageAudit.py --runtime
```

Remote shell uses GitHub Codespaces transport:

```bash
gh codespace ssh
```

No public SSH port is required.

## FFmpeg AI repair bay

Probe and seal the source identity:

```bash
python3 tools/ffmpegAiRepairBay.py probe clip.mp4
```

Demux exact frames and audio:

```bash
python3 tools/ffmpegAiRepairBay.py demux clip.mp4 "$PROFESSOR_GARAGE_CACHE/job-001"
```

Create a quick diagnostic sheet:

```bash
python3 tools/ffmpegAiRepairBay.py contact-sheet clip.mp4 "$PROFESSOR_GARAGE_CACHE/job-001/contact.jpg"
```

Place corrected frames in a repair directory using the original `shot%08d.png` names, then rebuild only that exact window:

```bash
python3 tools/ffmpegAiRepairBay.py rebuild-window \
  --source-frames "$PROFESSOR_GARAGE_CACHE/job-001/frames" \
  --repair-frames "$PROFESSOR_GARAGE_CACHE/job-001/repairs" \
  --output-frames "$PROFESSOR_GARAGE_CACHE/job-001/rebuilt" \
  --start-frame 117 \
  --end-frame 143
```

Remux with source audio:

```bash
python3 tools/ffmpegAiRepairBay.py remux \
  --frames "$PROFESSOR_GARAGE_CACHE/job-001/rebuilt" \
  --source clip.mp4 \
  --output clip-fixed-v1.mp4 \
  --fps 30
```

Create a side-by-side review candidate:

```bash
python3 tools/ffmpegAiRepairBay.py compare \
  --before clip.mp4 \
  --after clip-fixed-v1.mp4 \
  --output clip-compare-v1.mp4
```

## Boundaries

Source media is immutable. Repairs remain candidates. Google/other provider completion is not GREEN. Build-producing Forge work still requires explicit single-use Professor CAST. No merge, deploy, publication, or Crown is implied by a successful Codespace or repair command.
