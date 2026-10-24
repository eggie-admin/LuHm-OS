#!/usr/bin/env python3
"""Read-only GitHub Releases reconciliation for LuHm plugin download channels.

Only verified *published* release metadata with a ZIP + matching SHA256 asset
is surfaced. Android APKs, GitHub source archives and drafts never count as
ChatGPT plugin downloads. This script does not publish releases.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

REPO = "eggie-admin/LuHm-OS"
CHANNELS = ("proposed", "beta", "stable")
TAG = re.compile(r"^luhm-plugin-(proposed|beta|stable)-v([0-9]+\.[0-9]+\.[0-9]+)-s([0-9a-f]{8})$")
SHA = re.compile(r"^[0-9a-f]{64}$")
HOST = "https://github.com/" + REPO + "/releases/download/"


def channel_entry(release: dict) -> tuple[str, dict] | None:
    if not isinstance(release, dict) or release.get("draft") is not False:
        return None
    match = TAG.fullmatch(str(release.get("tag_name", "")))
    if not match:
        return None
    channel, version, short_sha = match.groups()
    if bool(release.get("prerelease")) != (channel != "stable"):
        return None
    tag = release["tag_name"]
    assets = release.get("assets") or []
    zips = [a for a in assets if isinstance(a, dict) and
            re.fullmatch(r"LuHmOS-ChatGPT-" + re.escape(channel) +
                         r"-v" + re.escape(version) + r"-s" + short_sha +
                         r"\.zip", str(a.get("name", ""))) and a.get("size", 0) > 0]
    if len(zips) != 1:
        return None
    package = zips[0]
    checks = [a for a in assets if isinstance(a, dict)
              and a.get("name") == package["name"] + ".sha256"
              and a.get("size", 0) > 0]
    if len(checks) != 1:
        return None
    expected = HOST + tag + "/" + package["name"]
    checksum = expected + ".sha256"
    if package.get("browser_download_url") != expected or checks[0].get("browser_download_url") != checksum:
        return None
    body = str(release.get("body") or "")
    if ("LUHM_PLUGIN_CHANNEL=" + channel) not in body or ("LUHM_PLUGIN_SOURCE_SHORT=" + short_sha) not in body:
        return None
    published = str(release.get("published_at") or "")
    if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", published):
        return None
    return channel, {
        "tag": tag, "version": version, "publishedAt": published,
        "download": expected, "sha256": checksum,
        "release": "https://github.com/" + REPO + "/releases/tag/" + tag,
        "sourceShort": short_sha,
        "deviceProof": "NOT_INFERRED_FROM_RELEASE",
        "pluginHostInstallProof": "NOT_INFERRED_FROM_RELEASE",
    }


def reconcile(releases: list) -> dict:
    if not isinstance(releases, list):
        raise ValueError("release response must be an array")
    current = {c: None for c in CHANNELS}
    for release in releases:
        result = channel_entry(release)
        if result is None:
            continue
        channel, entry = result
        previous = current[channel]
        if previous is None or (entry["publishedAt"], entry["tag"]) > (previous["publishedAt"], previous["tag"]):
            current[channel] = entry
    return {
        "schema": "luhmOs.pluginReleaseHub.v1",
        "repository": REPO,
        "source": "publishedGitHubReleasesOnly",
        "channels": current,
        "crownStatus": "NO_RUNTIME_OR_RELEASE_AUTHORITY",
    }


def markdown(data: dict) -> str:
    lines = [
        "# LuHm OS ChatGPT Plugin downloads",
        "",
        "Live release metadata is authoritative; package download does not install a plugin in ChatGPT.",
        "The iPhone tester needs a supported ChatGPT plugin invitation/install, not an APK or ZIP sideload.",
        "",
        "| Channel | Published version | Package | SHA-256 |",
        "| --- | --- | --- | --- |",
    ]
    for channel in CHANNELS:
        item = data["channels"][channel]
        if item:
            lines.append("| " + channel.title() + " | [" + item["version"] + "](" +
                         item["release"] + ") | [ZIP](" + item["download"] +
                         ") | [checksum](" + item["sha256"] + ") |")
        else:
            lines.append("| " + channel.title() + " | NOT PUBLISHED | No verified package | Not available |")
    lines += ["", "[GitHub Releases](https://github.com/" + REPO + "/releases)", "",
              "Only approved packages with matching checksum assets appear. Beta/Stable require separate host/device and Professor proof.", ""]
    return "\n".join(lines)


def load_live() -> list:
    url = "https://api.github.com/repos/" + REPO + "/releases?per_page=100"
    request = Request(url, headers={"Accept": "application/vnd.github+json",
                                    "Cache-Control": "no-cache",
                                    "User-Agent": "LuHm-Release-Hub-Audit"})
    with urlopen(request, timeout=12) as result:
        return json.load(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Offline fixture of GitHub API releases")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--require-channel", choices=CHANNELS)
    args = parser.parse_args()
    releases = json.loads(args.input.read_text(encoding="utf-8")) if args.input else load_live()
    data = reconcile(releases)
    print(json.dumps(data, indent=2) if args.format == "json" else markdown(data))
    return 1 if args.require_channel and data["channels"][args.require_channel] is None else 0


if __name__ == "__main__":
    raise SystemExit(main())
