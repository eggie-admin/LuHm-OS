"""Untrusted RSS and ZIP/JAR/7z transport tests, no network or writes."""
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import oneAppExchange as exchange

SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
RSS = b'<rss version="2.0"><channel><title>LuHm</title><item><title>A</title><link>https://example.org/a</link><description>Story</description></item></channel></rss>'
ATOM = b'<feed xmlns="http://www.w3.org/2005/Atom"><title>Wire</title><entry><title>A</title><link href="https://example.org/a"/><summary>Story</summary></entry></feed>'


class ExchangeTests(unittest.TestCase):
    def test_rss_envelope_roundtrip(self):
        feed = exchange.rss_to_json(RSS, SHA)
        self.assertEqual(feed["feedType"], "rss2")
        self.assertEqual(len(feed["items"]), 1)
        envelope = exchange.encode_envelope(feed, SHA)
        self.assertEqual(exchange.decode_envelope(envelope), feed)
        self.assertFalse(envelope["authenticated"])

    def test_atom_normalizes(self):
        self.assertEqual(exchange.rss_to_json(ATOM, SHA)["feedType"], "atom")
        self.assertEqual(exchange.rss_to_json(ATOM, SHA)["items"][0]["summary"], "Story")

    def test_dtd_rejected(self):
        with self.assertRaises(exchange.ExchangeError):
            exchange.rss_to_json(b'<!DOCTYPE rss [<!ENTITY bad "x">]>' + RSS, SHA)

    def test_http_and_credentials_rejected(self):
        for url in (b"http://evil.test/", b"https://user:secret@evil.test/"):
            with self.subTest(url=url):
                with self.assertRaises(exchange.ExchangeError):
                    exchange.rss_to_json(RSS.replace(b"https://example.org/a", url), SHA)

    def test_reject_overlarge_feed(self):
        with self.assertRaises(exchange.ExchangeError):
            exchange.rss_to_json(RSS + b"x" * exchange.MAX_RSS_BYTES, SHA)

    def test_utf16_dtd_rejected(self):
        raw = ('<!DOCTYPE rss><rss version="2.0"><channel/></rss>').encode("utf-16")
        with self.assertRaises(exchange.ExchangeError):
            exchange.rss_to_json(raw, SHA)

    def test_source_sha_rejected(self):
        with self.assertRaises(exchange.ExchangeError):
            exchange.rss_to_json(RSS, "main")

    def test_base64_tamper_and_noncanonical_rejected(self):
        envelope = exchange.encode_envelope(exchange.rss_to_json(RSS, SHA), SHA)
        envelope["sha256"] = "0" * 64
        with self.assertRaises(exchange.ExchangeError):
            exchange.decode_envelope(envelope)
        envelope["data"] += "*"
        with self.assertRaises(exchange.ExchangeError):
            exchange.decode_envelope(envelope)

    def test_zip_and_jar_inspection(self):
        with tempfile.TemporaryDirectory() as tmp:
            for suffix in ("zip", "jar"):
                path = Path(tmp) / ("source." + suffix)
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("META-INF/MANIFEST.MF", b"Manifest-Version: 1.0\n")
                receipt = exchange.inspect_archive(path, SHA)
                self.assertEqual(receipt["status"], "INSPECTED_ONLY")
                self.assertFalse(receipt["executed"])
                self.assertEqual(len(receipt["members"]), 1)

    def test_traversal_rejected_in_jar(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.jar"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("../escaping.class", b"bad")
            with self.assertRaises(exchange.ExchangeError):
                exchange.inspect_archive(path, SHA)

    def test_corrupt_jar_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "corrupt.jar"
            path.write_bytes(b"not a jar")
            with self.assertRaises(exchange.ExchangeError):
                exchange.inspect_archive(path, SHA)

    def test_7z_magic_is_blocked_no_extract(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.7z"
            path.write_bytes(bytes.fromhex("377abcaf271c") + b"fixture-not-a-real-archive")
            receipt = exchange.inspect_archive(path, SHA)
            self.assertEqual(receipt["status"], "BLOCKED_APPROVED_7Z_READER_REQUIRED")
            self.assertFalse(receipt["extracted"])

    def test_forged_7z_magic_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.7z"
            path.write_bytes(b"not 7zip")
            with self.assertRaises(exchange.ExchangeError):
                exchange.inspect_archive(path, SHA)


if __name__ == "__main__":
    unittest.main()
