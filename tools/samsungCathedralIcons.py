#!/usr/bin/env python3
"""Stage existing LuHm-OS horned-L Canon as Android launch and adaptive icons.

Source of art: publicationSite/logo.svg, mirrored in plugins/luhm-os/assets/logo.svg.
Only local PNG derivatives and public nonsecret hashes. No signing or publishing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "publicationSite/logo.svg"
PLUGIN_LOGO = ROOT / "plugins/luhm-os/assets/logo.svg"
PALETTE = {
    "background": (23, 19, 31, 255),
    "violet": (159, 122, 234, 255),
    "white": (247, 244, 255, 255),
}
ICON_NAMES = (
    ("main_192x192", "launcher192.png"),
    ("adaptive_foreground_432x432", "adaptiveForeground432.png"),
    ("adaptive_background_432x432", "adaptiveBackground432.png"),
    ("adaptive_monochrome_432x432", "adaptiveMonochrome432.png"),
)

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("RED_SAMSUNG_CANON_ICON:" + message)

def check_logo() -> str:
    raw = LOGO.read_bytes()
    require(raw == PLUGIN_LOGO.read_bytes(), "public-site and plugin logo source mismatch")
    text = raw.decode("utf-8")
    for anchor in ('viewBox="0 0 512 512"', 'M126 112l64 70-42 36-70-38z',
                   'M146 150h72v188h152v72H146z',
                   'cx="353" cy="315" r="34"',
                   '#17131f', '#9f7aea', '#f7f4ff'):
        require(anchor in text, "canonical horned-L SVG changed; review before raster staging:" + anchor)
    return hashlib.sha256(raw).hexdigest()

def inside(x: float, y: float, pts: list[tuple[float, float]]) -> bool:
    value = False
    for i, (ax, ay) in enumerate(pts):
        bx, by = pts[i - 1]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            value = not value
    return value

def symbol(u: float, v: float, monochrome: bool = False) -> tuple[int, int, int, int]:
    violet = PALETTE["white"] if monochrome else PALETTE["violet"]
    if (inside(u,v,[(126,112),(190,182),(148,218),(78,180)])
            or inside(u,v,[(386,112),(322,182),(364,218),(434,180)])):
        return violet
    if (146 <= u < 218 and 150 <= v < 410) or (146 <= u < 370 and 338 <= v < 410):
        return PALETTE["white"]
    if (u - 353)**2 + (v - 315)**2 < 34**2:
        return violet
    return (0, 0, 0, 0)

def rounded_rect(u: float, v: float, radius: float = 96) -> bool:
    if u < 0 or v < 0 or u >= 512 or v >= 512:
        return False
    cx = radius if u < radius else 512 - radius if u > 512 - radius else u
    cy = radius if v < radius else 512 - radius if v > 512 - radius else v
    return (u - cx)**2 + (v - cy)**2 <= radius**2

def at(x: float, y: float, n: int, style: str) -> tuple[int, int, int, int]:
    u, v = 512 * x / n, 512 * y / n
    if style == "main":
        if not rounded_rect(u, v):
            return (0, 0, 0, 0)
        mark = symbol(u, v)
        return mark if mark[3] else PALETTE["background"]
    if style == "background":
        return PALETTE["background"]
    # Adaptive icon symbol is deliberately reduced to the platform safe center area.
    source_u = 256 + (u - 256) / .73
    source_v = 256 + (v - 256) / .73
    return symbol(source_u, source_v, monochrome=(style == "monochrome"))

def make_png(n: int, style: str) -> bytes:
    def chunk(tag: bytes, raw: bytes) -> bytes:
        return struct.pack(">I", len(raw)) + tag + raw + struct.pack(">I", zlib.crc32(tag + raw) & 0xffffffff)
    pixels = []
    for y in range(n):
        row = bytearray(b"\0")
        for x in range(n):
            samples = (at(x + dx, y + dy, n, style)
                       for dx,dy in ((.25,.25),(.75,.25),(.25,.75),(.75,.75)))
            cs = list(samples)
            row.extend(bytes(sum(s[k] for s in cs)//4 for k in range(4)))
        pixels.append(bytes(row))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">2I5B", n, n, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(b"".join(pixels), 9)) +
            chunk(b"IEND", b""))

def stage_preset(preset: Path, icon_dir: Path) -> None:
    require(preset.is_file(), "Android export preset missing")
    data = preset.read_text(encoding="utf-8")
    require(icon_dir.is_relative_to(ROOT), "icon location must be beneath repository root")
    relative = icon_dir.relative_to(ROOT).as_posix()
    for key, filename in ICON_NAMES:
        old = f'launcher_icons/{key}=""'
        new = f'launcher_icons/{key}="res://{relative}/{filename}"'
        require(data.count(old) == 1, "non-blank or ambiguous existing Android icon; refuse overwrite:" + key)
        data = data.replace(old, new)
    preset.write_text(data, encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True, help="output folder inside checkout")
    parser.add_argument("--preset", type=Path, help="optional isolated Android export preset to mutate")
    args = parser.parse_args()
    source_sha = check_logo()
    out = args.output.resolve()
    require(out.is_relative_to(ROOT), "refuse writes outside checkout")
    out.mkdir(parents=True, exist_ok=True)
    definitions = (
        ("launcher192.png",192,"main"),
        ("adaptiveForeground432.png",432,"foreground"),
        ("adaptiveBackground432.png",432,"background"),
        ("adaptiveMonochrome432.png",432,"monochrome")
    )
    receipts = []
    for name,n,style in definitions:
        content = make_png(n, style)
        require(len(content) > 500, "icon unexpectedly empty:" + name)
        path = out / name
        path.write_bytes(content)
        receipts.append({"name":name,"pixels":[n,n],"sha256":hashlib.sha256(content).hexdigest()})
    if args.preset:
        stage_preset(args.preset.resolve(), out)
    receipt = {
        "schema":"luhmOs.samsungCathedralIconDerivatives.v1",
        "brand":"LuHm-OS",
        "sourceLogo":"publicationSite/logo.svg",
        "sourceLogoSha256":source_sha,
        "icons":receipts,
        "originalArtworkAuthoritative":True,
        "stage":"REVIEWED_SOURCE_DERIVATIVE_ONLY",
        "androidPackageSigned":False,
        "samsungDeviceProof":False,
        "publicReleaseApproved":False,
        "crownStatus":"STOP"
    }
    (out / "iconReceipt.json").write_text(json.dumps(receipt, indent=2)+"\n",encoding="utf-8")
    print("GREEN_SAMSUNG_CANON_ICON_DERIVATIVES_SOURCE_ONLY")
    print("NO_APK_SIGNING_OR_DEVICE_INSTALL_CLAIM")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        raise SystemExit(str(exc))
