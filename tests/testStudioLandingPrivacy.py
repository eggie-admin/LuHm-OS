#!/usr/bin/env python3
"""Read-only studio web source and publication firewall audit."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.titles=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="a" and "href" in attrs:self.links.append(attrs["href"])
        if tag=="title":self.titles.append("title")
class StudioSafety(unittest.TestCase):
    def test_public_file_exists_and_is_semantically_complete(self):
        content=(ROOT/"studioLanding/index.html").read_text()
        parser=Page();parser.feed(content)
        self.assertIn("under construction",content.lower())
        for brand in ["Pirate Daddy Studios","Pirate Daddy Film","Eggie Bagelface Art"]:
            self.assertIn(brand,content)
        self.assertIn("https://www.instagram.com/eggiebagelface/",parser.links)
        self.assertIn("mailto:eggiebagelface@gmail.com",parser.links)
        self.assertIn("title",parser.titles)
    def test_no_private_linked_locations(self):
        content=(ROOT/"studioLanding/index.html").read_text().lower()
        for forbidden in ["drive.google.com","docs.google.com","privkey.pem","github_pat_","cloudflare_api_token","sk-proj-","google_api_key","<iframe","<form","pirate-daddies-film/demo-repository"]:
            self.assertNotIn(forbidden,content)
    def test_canon_denies_publication_without_approval(self):
        c=json.loads((ROOT/"doctrine/studioPublicPrivateReleaseV1.json").read_text())
        self.assertEqual(c["canonicalDomain"],"eggiebagelface.art")
        self.assertEqual(len(c["brands"]),3)
        self.assertTrue(c["separation"]["neverLinkPrivateSourcesFromSite"])
        self.assertFalse(c["releaseAuthority"])
        self.assertFalse(any(c["externalMutation"].values()))
        self.assertEqual(c["crown"],"STOP_PENDING_PUBLIC_RUNTIME_AND_OWNER_APPROVAL")
if __name__=="__main__":unittest.main()
