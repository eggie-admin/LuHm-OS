# AI-FFmpeg local-first candidate

## Intent and scope

This **proposed** component adds FFmpeg introspection and a guarded local review renderer to the existing LuHm source. It does not replace the existing Google Cloud video worker, Godot/FFmpeg proof scripts, or Yume art-direction canon. It does not claim the Professor's Ubuntu service is running. Runtime installation, canon promotion, Drive archiving and publication remain separately gated.

## Discover all installed FFmpeg facilities

Run: `python3 host/ai-ffmpeg/ai-ffmpeg.py doctor --full`

This enumerates the actual host build's encoders, decoders, formats, muxers, demuxers, filters, protocols, hardware accelerators, codecs, pixel/sample formats, channel layouts, devices and bitstream filters. Availability is not GPU functionality proof. Real GPU output requires a separate device encode/decode smoke test. This version deliberately permits only an audited portrait MP4 preset, not arbitrary FFmpeg options or AI-generated shell commands.

## One review candidate

1. Keep source images and clips under `$HOME/hydra/media`; keep MP4 candidates under `$HOME/hydra/media/candidates`.
2. Copy `media/pirate-daddy-film/episode-template.json` to a private working location. Fill in seven local shot inputs, which cover five sections (400 has three shots). Do **not** add audio yet.
3. After Professor has reviewed the job and selected assets, set `reviewApproved` to `true` and run:

```bash
python3 host/ai-ffmpeg/ai-ffmpeg.py render --manifest "$HOME/hydra/media/episode.json" --approve-render
```

It produces an H.264/yuv420p silent vertical MP4 and a SHA-256 receipt next to the output. Both remain private candidates. The manifest accepts only local media with bounded paths, clip lengths and source file sizes. This is a CPU preview, not a full finishing pipeline.

## Local worker service (never deploy to a public Render URL)

Set a new random token in your private environment and start a loopback-only worker:

```bash
export LUHM_FFMPEG_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(36))')"
python3 host/ai-ffmpeg/ai-ffmpeg.py serve
```

Read-only probes: `curl --fail http://127.0.0.1:8797/healthz`, `/capabilities`, and `/presets`.
Authenticated rendering is only `POST /render` with a bearer token and `reviewApproved: true` in the JSON. Store tokens in `~/.secret/hydra` with user-only permissions for a permanent service; do not put them in the repo, logs, screenshots, plugins or browser. Never forward port 8797 from a router or bind publicly. This worker is intentionally single-job, not a public multi-tenant render farm.

## Next gates

- Verify Ubuntu's installed FFmpeg and NVIDIA GPU acceleration with an encode/decode smoke receipt before enabling a GPU preset.
- Add constrained audio mixing, captions, loudness normalization, subtitles, image-sequence and proxy presets individually, each with tests and Professor review. Audio stays deferred for *Into the Warp*.
- Connect the local cockpit through a verified authenticated local adapter. An Android or cloud client cannot directly access the workstation's loopback address.
- Render three distinct approved episodes, archive final binaries in Drive and record SHA/Drive pointers in GitHub. The renderer never publishes anything to Facebook automatically.
