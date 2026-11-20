# Reaper Scrub Desk | source-only workflow candidate

## Intent
A human editor selects and scrubs their own local video, marks IN/OUT and timestamps, then provides an edit-decision list (`Reaper_Edit_Decisions.json`) to the ChatGPT/Lum film portal. This uses real video, no AI face replacement, and never modifies protected camera originals.

## Demonstrated proof (2026-11-20)
- Self-contained `Reaper_Scrub_Desk.html` prototype stored in the connected Reaper Drive `03_video_edit` folder, with 2 compressed CC0 demo clips, local file picker, nominal single-frame seek, speed, IN/OUT, frame PNG and EDL JSON export.
- JavaScript parse passed Node `--check`; source examples were decoded, scaled and clipped with FFmpeg.
- A timestamped steel-mill contact sheet was extracted; files stored in Drive's video-editing folder.
- The exact Android browser/file-chooser and ChatGPT AppBlock controls are not yet device-verified. Don't claim live two-way video stream or unrestricted device control.

## Task flow
1. Artist scrubs video in local browser/AppBlock; original file remains local until explicitly attached/uploaded.
2. Artist sets IN/OUT, editor note, optionally captures screenshot, and exports EDL JSON.
3. Lum receives the human-selected EDL via message/attachment and maps `source` to original video in the approved private Drive vault.
4. Yume plans requested pacing, effects, dialogue, color-grade and soundtrack without changing approved masters.
5. Urd verifies source identity, rights, frame continuity, artifacts, and notes contradictions; Skuld diagnoses FFmpeg/GIMP/Blender/tooling blockers; Belldandy updates source and credits ledger.
6. FFmpeg locally or a bounded approved remote worker renders draft proxy and waveform/frames with timecodes; reviewer approves exact candidate. No public promotion without owner review.

## Format
`{schema:'pirateDaddyFilm.edl.v1',project:'Reaper Is My Only G',cuts:[{shotId,clip,time,in,out,frameRate,note,palette}]}`; numbers are seconds from file start. Browser frame step is approximate, not guaranteed sample-perfect. FFmpeg seek/cut output must be reverified.

## Security
The user-facing Drive art root currently inherits broad write sharing. Do not upload private originals to that tree. Use the previously verified owner-only Reaper masters vault. Never embed real original videos, medical records, addresses or third-party music in public GitHub, workflow artifacts, the plugin package or a published Site. Don't create unauthorized paid runs, camera access, automated web publishing, or continuous monitoring.

## Future iterations
Authenticated private browser preview with frame-accurate decode, shared timecoded annotations, EDL validation, FFmpeg proxy generation with per-frame contact sheets, SRT and audio waveform, diff/candidate receipts, and GitHub job orchestration on explicit command.
