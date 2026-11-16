#!/usr/bin/env python3
"""Original, bounded 8x8 planar tiles and text for LuHm-OS.

Inspired by documented NES/SNES graphics formats. Processes only caller-supplied
synthetic or owner-original pixels, never ROM, game, BIOS or firmware bytes.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

FORMATS = {"nes2bpp": (2, 16), "snes4bpp": (4, 32)}
CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .!?-:"
REF = re.compile(r"[0-9a-f]{40}\Z")


def _kind(name: Any) -> tuple[int, int]:
    if type(name) is not str or name not in FORMATS:
        raise ValueError("RED_RETRO_FORMAT")
    return FORMATS[name]


def encode_tile(pixels: Any, fmt: str = "nes2bpp") -> bytes:
    bpp, size = _kind(fmt)
    if (type(pixels) not in (list, tuple) or len(pixels) != 64 or
            any(type(x) is not int or not 0 <= x < 1 << bpp for x in pixels)):
        raise ValueError("RED_RETRO_PIXELS")
    out = bytearray(size)
    for row in range(8):
        for plane in range(bpp):
            packed = 0
            for col in range(8):
                packed |= ((pixels[row * 8 + col] >> plane) & 1) << (7 - col)
            if fmt == "nes2bpp":
                index = plane * 8 + row
            else:
                index = (plane // 2) * 16 + row * 2 + plane % 2
            out[index] = packed
    return bytes(out)


def decode_tile(raw: Any, fmt: str = "nes2bpp") -> list[int]:
    bpp, size = _kind(fmt)
    if type(raw) is not bytes or len(raw) != size:
        raise ValueError("RED_RETRO_TILE_BYTES")
    pix = [0] * 64
    for row in range(8):
        for plane in range(bpp):
            index = plane * 8 + row if fmt == "nes2bpp" else (
                (plane // 2) * 16 + row * 2 + plane % 2)
            byte = raw[index]
            for col in range(8):
                pix[row * 8 + col] |= ((byte >> (7 - col)) & 1) << plane
    return pix


def encode_tilemap(indices: Any) -> bytes:
    """Original 4x4 sheet map, NOT a retail NES/SNES nametable or ROM header."""
    if (type(indices) not in (list, tuple) or len(indices) != 16 or
            any(type(i) is not int or not 0 <= i <= 15 for i in indices)):
        raise ValueError("RED_RETRO_TILEMAP")
    return bytes(indices)


def encode_text(value: Any) -> bytes:
    """Restricted original ASCII glyph indexes, not proprietary game font tables."""
    if (type(value) is not str or not 1 <= len(value) <= 96 or
            any(c not in CHARSET for c in value)):
        raise ValueError("RED_RETRO_TEXT")
    return bytes(CHARSET.index(c) for c in value)


def decode_text(raw: Any) -> str:
    if (type(raw) is not bytes or not 1 <= len(raw) <= 96 or
            any(byte >= len(CHARSET) for byte in raw)):
        raise ValueError("RED_RETRO_GLYPHS")
    return "".join(CHARSET[i] for i in raw)


def original_sheet_receipt(*, pixels: Any, fmt: str, tilemap: Any,
                           text: str, rights: str, source_ref: str) -> dict[str, Any]:
    if rights != "originalOwned" or type(source_ref) is not str or not REF.fullmatch(source_ref):
        raise ValueError("RED_RETRO_RIGHTS_OR_SOURCE")
    if type(pixels) not in (list, tuple) or len(pixels) != 16:
        raise ValueError("RED_RETRO_SHEET_SIZE")
    encoded = [encode_tile(tile, fmt) for tile in pixels]
    map_bytes = encode_tilemap(tilemap)
    text_bytes = encode_text(text)
    return {
        "schema": "luhmOs.originalRetroTileReceipt.v1", "format": fmt,
        "tilePixels": 8, "tileCount": len(encoded),
        "spriteSheetWidthPixels": 32, "spriteSheetHeightPixels": 32,
        "sourceRef": source_ref,
        "tileDigestsSha256": [hashlib.sha256(b).hexdigest() for b in encoded],
        "sheetDigestSha256": hashlib.sha256(b"".join(encoded) + map_bytes + text_bytes).hexdigest(),
        "tilemapHex": map_bytes.hex(),
        "textGlyphHex": text_bytes.hex(),
        "paletteRightsVerified": False, "romRead": False, "retailSpritesImported": False,
        "firmwareTouched": False, "tileBinaryReturned": False,
        "status": "SYNTHETIC_OR_OWNED_ASSET_PLAN_ONLY",
        "publicationAuthorized": False, "greenAuthority": False,
    }


if __name__ == "__main__":
    blank = [[0] * 64 for _ in range(16)]
    print(json.dumps(original_sheet_receipt(
        pixels=blank, fmt="nes2bpp", tilemap=list(range(16)),
        text="MOONLIT ARCHIVE", rights="originalOwned",
        source_ref="0" * 40), indent=2))
