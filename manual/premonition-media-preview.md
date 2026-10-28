# LuHm-OS: Project Premonition | VLC and FFmpeg local media adapter

**Mutation ⑤ source slice** for the artist-first studio. The browser defaults to native HTML5 playback for manually selected local MP4/WebM/music; no VLC web server or plugin is needed. The Babylon world + Vue scene editor + jQuery bridge remain independently operable.

### What is implemented in this candidate
- Local media picker: MP4/WebM video and MP3/WAV/OGG/M4A audio. Browser creates and revokes object URLs, never uploads media or exposes local filenames in typed events. Browser codec support varies; a matching extension is not decoding proof.
- Small jQuery typed event `luhm:media:preview` for UI coordination, without Python/SQL/Crown privileges. This is separate from the protected cockpit source.
- Read-only Python `ffprobe` scanner for an already-approved local media file, returning stream codec, SHA256, size and duration. Restricts paths to a selected root; never accepts an arbitrary URL or traverses out to private files.
- Optional external desktop VLC launch **only** when directly requested by an operator with `--play-vlc --approved`. Requires an already installed VLC and display environment. No `--extraintf http`, no saved credentials or network listener; launch is not a verified playback receipt.
- Existing review-gated `host/ai-ffmpeg/ai-ffmpeg.py` remains authoritative for actual video processing. This preview stage does **not** bypass its render approval or claim that a complete FFmpeg → VLC automation has been validated.

### Operator usage on a controlled Linux desktop
```bash
python3 tools/premonitionMediaPreview.py --root /path/to/approved-media --file shot.mp4
python3 tools/premonitionMediaPreview.py --root /path/to/approved-media --file shot.mp4 --play-vlc --approved
```
The first invocation uses FFprobe to inspect metadata and returns a bounded receipt. The second explicitly starts an optional local VLC process; it does not assert image/audio quality or successful playback. No desktop VLC is required for the default HTML5 candidate.

### Gate before production release
1. Verify a rights-cleared FFmpeg-rendered MP4/audio from existing worker through real browser preview, play, pause, seek, and end-of-stream, with checksum and clean local source path.
2. Test desktop VLC playback on an approved host with updated VLC, a correctly installed LibVLC or binary, video/audio sink and device-specific codecs.
3. Measure Samsung WebView HTML5 playback, object picker handling, RAM/GPU/FPS and coexistence with Babylon/Godot. **APK not yet built or signed.**
4. Keep user-provided songs and character art local/private. Never proxy a YouTube stream, expose VLC HTTP control or publish media without rights clearance.
5. Only create a real F-Droid package after Android signer custody, separate F-Droid index signer and physical update proof.

**Source-only tests are not playback, Samsung installation or Crown evidence.**
