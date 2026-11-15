#!/usr/bin/env python3
"""Fail-closed public comeback media/caption test. No network or platform writes."""
from pathlib import Path
import hashlib
import unittest
ROOT=Path(__file__).resolve().parents[1]
IMG=ROOT/"studioLanding/media/eggie-studio-still-here-2026-11-15.jpg"
COPY=ROOT/"campaign/instagramReturn20261115.md"

class InstagramComebackSafety(unittest.TestCase):
    def test_public_image_is_real_jpeg(self):
        data=IMG.read_bytes()
        self.assertTrue(data.startswith(bytes.fromhex("ffd8ff")))
        self.assertTrue(data.endswith(bytes.fromhex("ffd9")))
        self.assertGreater(len(data),40_000)
        self.assertLess(len(data),8_000_000)
        print("PUBLIC_JPEG_SHA256="+hashlib.sha256(data).hexdigest())
    def test_approval_is_one_post_only(self):
        text=COPY.read_text()
        for phrase in ["APPROVED FOR PUBLICATION BY PROFESSOR SCOPED CAST",
                       "@eggiebagelface", "Still here.", "Pirate Daddy Studios",
                       "Pirate Daddy Film", "Eggie Bagelface Art"]:
            self.assertIn(phrase,text)
        self.assertIn("not a multi-platform broadcast",text)
        self.assertNotIn("sk-proj-",text.lower())
        self.assertNotIn("PRIVATE KEY",text)
        self.assertNotIn("PUBLISHED VERIFIED",text)
if __name__=="__main__":unittest.main()
