#!/usr/bin/env python3
"""Label rendered review images and fail if neutral/morphed frames match.

Intermediate PNG files stay only in the ephemeral runner; published artifact
contains derived WebP previews and proof JSON only, not the source GLB.
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont

PANELS = [
    ("neutralFront", "FRONT / ORIGINAL"),
    ("morphedFront", "FRONT / MORPH x0.80"),
    ("morphedFace", "FACE / MORPH x0.80"),
    ("neutralQuarter", "THREE-QUARTER / ORIGINAL"),
    ("morphedQuarter", "THREE-QUARTER / MORPH"),
    ("morphedPose", "THREE-QUARTER / POSE STRESS")
]

def main():
    source, output = (Path(p) for p in sys.argv[1:])
    output.mkdir(parents=True, exist_ok=True)
    previews = {name: Image.open(source / (name + ".png")).convert("RGB") for name, label in PANELS}
    measures = {}
    for baseline, candidate in (("neutralFront", "morphedFront"), ("neutralQuarter", "morphedQuarter")):
        diff = ImageChops.difference(previews[baseline], previews[candidate])
        box = diff.getbbox()
        pixel_count = sum(1 for pix in diff.getdata() if max(pix) > 5)
        measures[baseline + "_vs_" + candidate] = {"changedPixels": pixel_count, "diffBounds": box}
        if pixel_count < 35:
            raise SystemExit("RED_LUM_VISUAL: frames too similar, not proved: " + baseline)
    width, height = previews["neutralFront"].size
    caption_h = 42
    sheet = Image.new("RGB", (width * 3, (height + caption_h) * 2), (11, 10, 24))
    draw = ImageDraw.Draw(sheet)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 15) if Path(font_path).exists() else ImageFont.load_default()
    for idx, (name, title) in enumerate(PANELS):
        cx, cy = idx % 3, idx // 3
        left, top = cx * width, cy * (height + caption_h)
        sheet.paste(previews[name], (left, top + caption_h))
        draw.rectangle((left, top, left + width, top + caption_h), fill=(22, 21, 44))
        draw.text((left + 12, top + 12), title, fill=(90, 233, 214) if "MORPH" in title else (221, 191, 239), font=font)
    temp_sheet = output / "lumVisualReviewTemporary.png"
    sheet.save(temp_sheet)
    (output / "visualComparisonReceipt.json").write_text(json.dumps({
        "schema": "luhmOs.lumMorphPhase2VisualCompare.v1",
        "pixelChangeChecks": measures,
        "facesAndClippingHumanReviewRequired": True,
        "crown": "STOP",
        "status": "AWAITING_PROFESSOR_VISUAL_REVIEW",
    }, indent=2) + "\n")
    print("LUM_VISUAL_COMPARE_GREEN", json.dumps(measures), flush=True)

if __name__ == "__main__":
    main()
