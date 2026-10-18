# AI-FFmpeg local-first candidate

## Intent and scope

This **proposed** component adds FFmpeg introspection and a guarded local review renderer to the existing LuHm source. It does not replace the existing Google Cloud video worker, Godot/FFmpeg proof scripts, or Yume art-direction canon. It does not claim the Professor's Ubuntu service is running. Runtime installation, canon promotion, Drive archiving and publication remain separately gated.

## Discover all installed FFmpeg facilities

Run: `python3 host/ai-ffmpeg/ai-ffmpeg.py doctor --full`

This enumerates the actual host build's encoders, decoders, formats, muxers, demuxers, filters, protocols, hardware accelerators, codecs, pixel/sample formats, channel layouts, devices and bitstream filters. Availability is not GPU functionality proof. Real GPU output requires a separate device encode/decode smoke test. This version deliberately permits only an audited portrait MP4 preset, not arbitrary FFmpeg options or AI-generated shell commands.

## One review candidate

1. Keep source images and clips under `$HOME/hydra/media`; keep MP4 candidates under `$HOME/hydra/media/candidates`.
2. Copy `media/pirate-daddy-film/episode-template.json` to a private working location. Fill in seven local shot inputs, which cover five sections (400 has three shots). Keep any title-card still as the final shot input.
3. After Professor has reviewed the job and selected assets, set `reviewApproved` to `true` and run:

```bash
python3 host/ai-ffmpeg/ai-ffmpeg.py render --manifest "$HOME/hydra/media/episode.json" --approve-render
```

It produces an H.264/yuv420p vertical MP4 and a SHA-256 receipt next to the output. Both remain private candidates. The manifest accepts only local media with bounded paths, clip lengths and source file sizes. This is a CPU review renderer, not a full finishing pipeline.

For a reviewed music-backed cut, add this optional object to the manifest. `source` must be a local audio file under the input root, and the selected track segment must cover the full cut. The start offset selects where the soundtrack begins; volume is limited to 0–1; the fade duration is bounded to 10 seconds and the cut length.

```json
"audioBed": {
  "source": "blessed-is-the-swarm-review.wav",
  "startSeconds": 0,
  "volume": 0.75,
  "fadeOutSeconds": 1.5
},
"videoFadeOutSeconds": 1.5
```

`videoFadeOutSeconds` fades the final shot to black. Use the final shot for the title-card image, so the card fades with the picture. Rendering still requires both explicit `reviewApproved: true` in the manifest and the local `--approve-render` switch. A soundtrack is a private local input; the renderer does not fetch music, infer licensing, publish, or approve the result.

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
- Add captions, loudness normalization, subtitles, image-sequence and proxy presets individually, each with tests and Professor review.
- Connect the local cockpit through a verified authenticated local adapter. An Android or cloud client cannot directly access the workstation's loopback address.
- Render three distinct approved episodes, archive final binaries in Drive and record SHA/Drive pointers in GitHub. The renderer never publishes anything to Facebook automatically.

## Optional persistent Ubuntu user service

From this same checked-out candidate repository, after explicitly choosing to install a local systemd user service, run:

```bash
bash scripts/ai-ffmpeg-user-service.sh install
```

It creates a private random bearer token, a user-level systemd unit (not a root daemon), restricts filesystem writes and network to the local machine, enables automatic start while the user session is active, and attempts to start the service now. It refuses to overwrite an existing unit. Check status:

```bash
bash scripts/ai-ffmpeg-user-service.sh status
```

The installer must be run on the Professor's Ubuntu workstation. CI checks shell syntax only and does not claim the desktop service was installed or started. GPU access is intentionally disabled for this CPU-preview systemd candidate until separately tested.
