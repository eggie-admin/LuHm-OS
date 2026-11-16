#!/usr/bin/env python3
"""Retro source-only 8x8 NES/SNES planar format and original 4x4 sheet checks."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"tools/retroTileTextCodec.py"
s=importlib.util.spec_from_file_location("retroTileTextCodec",P)
assert s and s.loader
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)


class TestOriginalRetro(unittest.TestCase):
    def test_nes_2bit_plane_exact_single_pixel(self):
        pixels=[0]*64
        pixels[0]=3
        raw=m.encode_tile(pixels,"nes2bpp")
        self.assertEqual(len(raw),16)
        self.assertEqual(raw[0],128)
        self.assertEqual(raw[8],128)
        self.assertEqual(raw[1:8],bytes(7))
        self.assertEqual(m.decode_tile(raw,"nes2bpp"),pixels)

    def test_snes_4bit_plane_exact_single_pixel(self):
        pixels=[0]*64
        pixels[0]=15
        raw=m.encode_tile(pixels,"snes4bpp")
        self.assertEqual(len(raw),32)
        self.assertEqual([raw[i] for i in (0,1,16,17)],[128]*4)
        self.assertEqual(m.decode_tile(raw,"snes4bpp"),pixels)

    def test_four_by_four_all_tiles_and_original_text(self):
        tiles=[[i]*64 for i in range(16)]
        x=m.original_sheet_receipt(
            pixels=tiles,fmt="snes4bpp",tilemap=list(range(16)),
            text="MOONLIT ARCHIVE!",rights="originalOwned",
            source_ref="a"*40)
        self.assertEqual(x["tileCount"],16)
        self.assertEqual((x["spriteSheetWidthPixels"],x["spriteSheetHeightPixels"]),(32,32))
        self.assertEqual(x["tilemapHex"],bytes(range(16)).hex())
        self.assertEqual(m.decode_text(bytes.fromhex(x["textGlyphHex"])),"MOONLIT ARCHIVE!")
        self.assertEqual(len(x["sheetDigestSha256"]),64)
        self.assertFalse(x["romRead"])
        self.assertFalse(x["tileBinaryReturned"])
        self.assertFalse(x["publicationAuthorized"])

    def test_no_implicit_quantization_byte_overflow_or_lax_encoding(self):
        for bad in ([0]*63,[0]*63+[4],[0]*63+[True],b"\x00"*64):
            with self.subTest(bad=repr(bad)[:30]),self.assertRaises(ValueError):
                m.encode_tile(bad,"nes2bpp")
        for fmt,raw in (("nes2bpp",bytes(17)),("snes4bpp",bytes(16)),("tileHack",bytes(16))):
            with self.assertRaises(ValueError):
                m.decode_tile(raw,fmt)
        for bad in ("","lowercase","HELLO 🎮","A"*97,"A\x00"):
            with self.assertRaises(ValueError):
                m.encode_text(bad)
        with self.assertRaises(ValueError):
            m.decode_text(b"\xff")

    def test_no_retail_asset_claim_or_unregistered_tilemap(self):
        tiles=[[0]*64 for _ in range(16)]
        for opts in (
            {"rights":"abandonware"},
            {"source_ref":"main"},
            {"tilemap":[0]*15},
            {"pixels":tiles[:15]},
            {"fmt":"unknown"},
        ):
            with self.subTest(opts=str(opts)[:70]), self.assertRaises(ValueError):
                m.original_sheet_receipt(**{
                    "pixels":tiles,"fmt":"nes2bpp","tilemap":[0]*16,
                    "text":"LUM","rights":"originalOwned","source_ref":"a"*40,
                    **opts,
                })

if __name__=="__main__":
    unittest.main()
