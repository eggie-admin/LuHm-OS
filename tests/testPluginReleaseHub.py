"""Fail-closed release hub tests: latest of each verified channel only."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("hub", Path(__file__).resolve().parents[1] / "tools/pluginReleaseHub.py")
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


def sample(channel="proposed", version="1.0.2", short="a1b2c3d4", date="2026-10-20T12:00:00Z"):
    tag = "luhm-plugin-" + channel + "-v" + version + "-s" + short
    base = "https://github.com/eggie-admin/LuHm-OS/releases/download/" + tag + "/"
    name = "LuHmOS-ChatGPT-" + channel + "-v" + version + "-s" + short + ".zip"
    return {
        "draft": False, "tag_name": tag, "prerelease": channel != "stable",
        "body": "LUHM_PLUGIN_CHANNEL=" + channel + "\nLUHM_PLUGIN_SOURCE_SHORT=" + short,
        "published_at": date,
        "assets": [
            {"name": name, "size": 24000, "browser_download_url": base + name},
            {"name": name + ".sha256", "size": 132, "browser_download_url": base + name + ".sha256"},
        ],
    }


class PluginReleaseHubTest(unittest.TestCase):
    def test_empty_is_honestly_pending(self):
        data = hub.reconcile([])
        self.assertTrue(all(v is None for v in data["channels"].values()))
        self.assertIn("NOT PUBLISHED", hub.markdown(data))

    def test_latest_per_channel_not_one_global_latest(self):
        items = [
            sample("proposed", "1.0.1", "11223344", "2026-10-21T00:00:00Z"),
            sample("proposed", "1.0.2", "22334455", "2026-10-22T00:00:00Z"),
            sample("beta", "1.0.0", "33445566", "2026-10-19T00:00:00Z"),
            sample("stable", "0.9.0", "44556677", "2026-10-18T00:00:00Z"),
        ]
        result = hub.reconcile(items)["channels"]
        self.assertEqual(result["proposed"]["version"], "1.0.2")
        self.assertEqual(result["beta"]["version"], "1.0.0")
        self.assertEqual(result["stable"]["version"], "0.9.0")

    def test_android_apk_does_not_count(self):
        result = hub.reconcile([{"tag_name": "android-web3-abcd", "draft": False, "prerelease": True,
                                 "assets": [{"name": "x.apk", "size": 100}]}])
        self.assertIsNone(result["channels"]["proposed"])

    def test_draft_not_public(self):
        data = sample()
        data["draft"] = True
        self.assertIsNone(hub.reconcile([data])["channels"]["proposed"])

    def test_no_checksum_is_not_downloadable(self):
        data = sample()
        data["assets"] = data["assets"][:1]
        self.assertIsNone(hub.reconcile([data])["channels"]["proposed"])

    def test_fake_asset_url_denied(self):
        data = sample()
        data["assets"][0]["browser_download_url"] = "https://evil.example/file.zip"
        self.assertIsNone(hub.reconcile([data])["channels"]["proposed"])

    def test_stable_must_not_be_prerelease(self):
        data = sample("stable")
        data["prerelease"] = True
        self.assertIsNone(hub.reconcile([data])["channels"]["stable"])

    def test_prerelease_cannot_be_marked_latest_stable(self):
        data = sample("beta")
        data["prerelease"] = False
        self.assertIsNone(hub.reconcile([data])["channels"]["beta"])

    def test_no_forged_publication_receipt(self):
        data = sample()
        data["body"] = "hello"
        self.assertIsNone(hub.reconcile([data])["channels"]["proposed"])


if __name__ == "__main__":
    unittest.main()
