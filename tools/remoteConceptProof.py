#!/usr/bin/env python3
"""GitHub-hosted synthetic proof. Does not consume private Drive art."""
import hashlib
import json
import subprocess
from pathlib import Path

STORY = [
    ("100", "PIRATE DADDYS FILM", 2, "0x09131d"),
    ("200", "INCOMING TRANSMISSION", 2, "0x15202b"),
    ("300", "THE WARP OPENS", 3, "0x170e24"),
    ("401", "THE OLD GUARD", 3, "0x181d26"),
    ("402", "BIG DADDY", 3, "0x261021"),
    ("403", "WITCHING HOUR", 3, "0x0d2531"),
    ("500", "ROOT ACCESS: ANTI-DADDY", 2, "0x040409"),
]

def call(args):
    subprocess.run(args, check=True, stdin=subprocess.DEVNULL, timeout=180)

def main():
    out = Path("proof-artifacts")
    out.mkdir(exist_ok=True)
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    parts = []
    for index, (shot, title, seconds, color) in enumerate(STORY):
        part = out / ("shot-" + shot + ".mp4")
        video_filter = ("drawtext=fontfile=" + font + ":text='" + title +
                        "':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=(h-text_h)/2")
        call(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
              "-f", "lavfi", "-i", f"color=c={color}:s=720x1280:r=30:d={seconds}",
              "-vf", video_filter, "-an", "-c:v", "libx264", "-threads", "2",
              "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", str(part)])
        parts.append(part)
    concat = out / "concat.txt"
    concat.write_text("".join("file '" + x.name + "'\n" for x in parts))
    final = out / "pirate-daddy-concept-tech-proof.mp4"
    call(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
          "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy",
          "-movflags", "+faststart", str(final)])
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                    "format=duration:stream=codec_name,width,height",
                                    "-of", "json", str(final)], text=True)
    data = json.loads(probe)
    v = data["streams"][0]
    duration = float(data["format"]["duration"])
    assert v["codec_name"] == "h264" and (v["width"], v["height"]) == (720, 1280)
    assert 17.5 <= duration <= 18.5
    digest = hashlib.sha256(final.read_bytes()).hexdigest()
    receipt = {"schema": "luhm.remoteProofReceipt.v1", "status": "TECHNICAL_PROOF_ONLY",
               "title": "Pirate Daddy synthetic storyboard", "sha256": digest,
               "durationSeconds": duration, "shotIds": [x[0] for x in STORY],
               "sourceMedia": "generated-color-cards", "characterAnimationProven": False,
               "musicIncluded": False, "publicationApproved": False}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()
