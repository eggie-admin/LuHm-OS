"""Source-only checks for the public Studio front door. No network or private assets."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "studioPortal" / "index.html"
CANON = ROOT / "doctrine" / "studioHousePublicPrivateV1.json"


class Visitor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.scripts = []
        self.images = []
        self.inline_events = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "script":
            self.scripts.append(a.get("src", "inline"))
        if tag in ("iframe","img","video","audio"):
            self.images.append(tag)
        self.inline_events.extend(k for k in a if k.lower().startswith("on"))


class StudioSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = SITE.read_text(encoding="utf-8")
        cls.canon = json.loads(CANON.read_text(encoding="utf-8"))
        cls.parser = Visitor()
        cls.parser.feed(cls.html)

    def test_canonical_domain_and_public_working_names(self):
        self.assertEqual(self.canon["canonicalDomain"], "eggiebagelface.art")
        for brand in ["Pirate Daddy Studios","Pirate Daddy Film","Eggie Bagelface Art"]:
            self.assertIn(brand, [i["publicDisplay"] for i in self.canon["brands"]])
            self.assertIn(brand, re.sub(r"<[^>]+>", " ", self.html).replace("\n", " "))

    def test_under_construction_in_public_copy(self):
        self.assertIn("Studio under construction", self.html)
        self.assertIn("under construction", self.html)
        self.assertIn('lang="en"', self.html)
        self.assertIn('name="viewport"', self.html)
        self.assertIn("prefers-reduced-motion", self.html)
        self.assertIn("aria-label", self.html)

    def test_reachable_known_identity_and_contact(self):
        self.assertTrue(any(x.startswith("mailto:eggiebagelface@gmail.com") for x in self.parser.links))
        self.assertIn("https://www.instagram.com/eggiebagelface/", self.parser.links)

    def test_no_private_material_or_unproven_alias(self):
        self.assertEqual(self.parser.scripts, [])
        self.assertEqual(self.parser.images, [])
        self.assertEqual(self.parser.inline_events, [])
        for token in ("drive.google.com", "docs.google.com", "BEGIN PRIVATE KEY", "cloudflare-api",
                      "luHmOsAssets", "meta_access_token", "private asset link", "support@eggiebagelface.art"):
            self.assertNotIn(token.lower(), self.html.lower())

    def test_release_gate_is_not_proclaimed_live(self):
        self.assertFalse(self.canon["public"]["deployment"]["customDomainActive"])
        self.assertFalse(self.canon["public"]["deployment"]["liveHttpProof"])
        self.assertFalse(self.canon["release"]["metaPostPublication"])
        self.assertFalse(self.canon["release"]["privateMediaPublication"])


if __name__ == "__main__":
    unittest.main()
