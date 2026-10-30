#!/usr/bin/env python3
"""Offline, untrusted-file ingress contract for a proposed LuHm one-app shell.

No network, shell, extraction, API calls, DB writes, upgrades, or promotion.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import archiveIntake

MAX_RSS_BYTES = 1024 * 1024
MAX_JSON_BYTES = 256 * 1024
MAX_ITEMS = 128
MAX_FIELD = 8192
HEX_SHA = re.compile(r"^[0-9a-f]{40}$")
BASE64URL = re.compile(r"^[A-Za-z0-9_-]+$")
ATOM_NS = "{http://www.w3.org/2005/Atom}"


class ExchangeError(ValueError):
    pass


def stable_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def check_source_sha(source_sha: str) -> str:
    if not isinstance(source_sha, str) or HEX_SHA.fullmatch(source_sha) is None:
        raise ExchangeError("exact lowercase 40-character Git SHA required")
    return source_sha


def clipped_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    text = " ".join("".join(element.itertext()).split())
    if len(text) > MAX_FIELD:
        raise ExchangeError("RSS/Atom field too large")
    return text


def safe_link(url: str) -> str:
    if len(url) > 2048 or (url and not url.startswith("https://")):
        raise ExchangeError("only bounded HTTPS feed links are accepted")
    host = url.split("/", 3)[2] if url.startswith("https://") else ""
    if any(ord(ch) < 0x20 for ch in url) or "@" in host or not host and url:
        raise ExchangeError("link control characters or embedded credentials")
    return url


def rss_to_json(payload: bytes, source_sha: str) -> dict:
    """Normalize a local RSS 2.0 or Atom document, never fetch links."""
    check_source_sha(source_sha)
    if not isinstance(payload, bytes) or not 0 < len(payload) <= MAX_RSS_BYTES:
        raise ExchangeError("feed payload size invalid")
    if b"\x00" in payload or payload.startswith((b"\xff\xfe", b"\xfe\xff")):
        raise ExchangeError("UTF-16/XML null-byte encoding forbidden")
    low = payload.lower()
    if b"<!doctype" in low or b"<!entity" in low:
        raise ExchangeError("XML DTD/entities forbidden")
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ExchangeError("invalid feed XML") from exc
    if root.tag == "rss" and root.attrib.get("version") in ("2.0", "2.0.1"):
        channel = root.find("channel")
        if channel is None:
            raise ExchangeError("RSS channel missing")
        title = clipped_text(channel.find("title"))
        items = channel.findall("item")
        def normalize(node: ET.Element) -> dict:
            return {"title": clipped_text(node.find("title")),
                    "link": safe_link(clipped_text(node.find("link"))),
                    "summary": clipped_text(node.find("description")),
                    "published": clipped_text(node.find("pubDate"))}
        feed_type = "rss2"
    elif root.tag == ATOM_NS + "feed":
        title = clipped_text(root.find(ATOM_NS + "title"))
        items = root.findall(ATOM_NS + "entry")
        def normalize(node: ET.Element) -> dict:
            links = [el.get("href", "") for el in node.findall(ATOM_NS + "link")
                     if el.get("rel", "alternate") == "alternate"]
            return {"title": clipped_text(node.find(ATOM_NS + "title")),
                    "link": safe_link(links[0] if links else ""),
                    "summary": clipped_text(node.find(ATOM_NS + "summary") if node.find(ATOM_NS + "summary") is not None else node.find(ATOM_NS + "content")),
                    "published": clipped_text(node.find(ATOM_NS + "published") if node.find(ATOM_NS + "published") is not None else node.find(ATOM_NS + "updated"))}
        feed_type = "atom"
    else:
        raise ExchangeError("only RSS 2.0 and Atom 1.0 supported")
    if len(items) > MAX_ITEMS:
        raise ExchangeError("feed item count exceeds limit")
    normalized = []
    for item in items:
        row = normalize(item)
        row["id"] = hashlib.sha256(stable_json(row)).hexdigest()
        normalized.append(row)
    return {"schema": "luhmOs.oneAppFeed.v1", "sourceRef": source_sha,
            "feedType": feed_type, "title": title, "items": normalized,
            "networkAccess": False, "promotion": False, "crownStatus": "STOP"}


def encode_envelope(document: dict, source_sha: str) -> dict:
    """Base64url is transport encoding, not encryption, signature or authority."""
    check_source_sha(source_sha)
    if not isinstance(document, dict) or document.get("sourceRef") != source_sha:
        raise ExchangeError("document/source SHA mismatch")
    raw = stable_json(document)
    if len(raw) > MAX_JSON_BYTES:
        raise ExchangeError("JSON document too large")
    return {"schema": "luhmOs.oneAppEnvelope.v1", "sourceRef": source_sha,
            "encoding": "base64url-no-padding", "data": base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii"),
            "sha256": hashlib.sha256(raw).hexdigest(), "authenticated": False, "crownStatus": "STOP"}


def decode_envelope(envelope: dict) -> dict:
    if not isinstance(envelope, dict) or envelope.get("schema") != "luhmOs.oneAppEnvelope.v1":
        raise ExchangeError("invalid envelope schema")
    sha = check_source_sha(envelope.get("sourceRef"))
    data = envelope.get("data")
    if not isinstance(data, str) or len(data) > MAX_JSON_BYTES * 2 or BASE64URL.fullmatch(data) is None:
        raise ExchangeError("invalid base64url payload")
    try:
        raw = base64.b64decode(data + "=" * (-len(data) % 4), altchars=b"-_", validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ExchangeError("invalid base64url encoding") from exc
    if len(raw) > MAX_JSON_BYTES or base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") != data:
        raise ExchangeError("noncanonical or oversized envelope")
    if hashlib.sha256(raw).hexdigest() != envelope.get("sha256"):
        raise ExchangeError("payload hash mismatch")
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ExchangeError("invalid JSON envelope") from exc
    if not isinstance(result, dict) or result.get("sourceRef") != sha:
        raise ExchangeError("decoded source mismatch")
    return result


def inspect_archive(path: Path, source_sha: str) -> dict:
    """Read-only ZIP/JAR manifest; .7z is quarantined until a pinned extractor exists."""
    check_source_sha(source_sha)
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ExchangeError("archive must be a regular non-symlink file")
    ext = path.suffix.lower()
    if ext not in (".zip", ".jar", ".7z"):
        raise ExchangeError("unsupported archive extension")
    size = path.stat().st_size
    if size > min(archiveIntake.MAX_ARCHIVE_TOTAL, 128 * 1024 * 1024):
        raise ExchangeError("archive too large")
    receipt = {"schema": "luhmOs.oneAppArchive.v1", "sourceRef": source_sha,
               "archiveType": ext[1:], "archiveSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "extracted": False, "executed": False, "promotion": False, "crownStatus": "STOP"}
    if ext == ".7z":
        with path.open("rb") as reader:
            magic = reader.read(6)
        if magic != bytes.fromhex("377abcaf271c"):
            raise ExchangeError("invalid 7z magic")
        receipt.update({"status": "BLOCKED_APPROVED_7Z_READER_REQUIRED", "members": []})
        return receipt
    try:
        members = [{"path": name, "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
                   for name, blob in archiveIntake.zip_members(path)]
    except (OSError, ValueError, archiveIntake.IntakeError, zipfile.BadZipFile) as exc:
        raise ExchangeError("archive refused by safe ZIP intake") from exc
    receipt.update({"status": "INSPECTED_ONLY", "members": members})
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--feed", type=Path)
    group.add_argument("--archive", type=Path)
    parser.add_argument("--source-sha", required=True)
    args = parser.parse_args(argv)
    try:
        if args.feed:
            feed = rss_to_json(args.feed.read_bytes(), args.source_sha)
            result = {"feed": feed, "envelope": encode_envelope(feed, args.source_sha)}
        else:
            result = inspect_archive(args.archive, args.source_sha)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ExchangeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc), "crownStatus": "STOP"}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
