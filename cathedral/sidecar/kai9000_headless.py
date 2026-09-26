#!/usr/bin/env python3
"""Dependency-free Termux helper for bounded local Ollama requests.

This is a CLI adapter, not a network listener. It talks only to the loopback
Ollama API and can append inactive memory candidates to local Termux state.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import time
from urllib import parse, request

MAX_BODY = 256 * 1024
MAX_MESSAGE = 12000
DEFAULT_OLLAMA = "http://127.0.0.1:11434"
STATE_DIR = Path(os.environ.get("KAI9000_STATE_DIR", str(Path.home() / ".local/state/luhm/kai9000")))
MEMORY_FILE = STATE_DIR / "memory-candidates.jsonl"


def validate_base(url: str) -> str:
    parsed = parse.urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Ollama URL must be loopback HTTP")
    return url.rstrip("/")


def ollama_json(path: str, payload: dict | None = None, timeout: float = 15.0) -> dict:
    base = validate_base(os.environ.get("OLLAMA_URL", DEFAULT_OLLAMA))
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    req = request.Request(base + path, data=data, headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=timeout) as response:
        raw = response.read(MAX_BODY + 1)
    if len(raw) > MAX_BODY:
        raise ValueError("Ollama response too large")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Ollama response must be an object")
    return value


def models() -> list[str]:
    doc = ollama_json("/api/tags", timeout=3.0)
    return sorted(str(m.get("name")) for m in doc.get("models", []) if isinstance(m, dict) and m.get("name"))


def chat(model: str, message: str) -> dict:
    if not message or len(message) > MAX_MESSAGE:
        raise ValueError("message length invalid")
    available = models()
    if model not in available:
        raise ValueError("model is not currently installed")
    doc = ollama_json("/api/chat", {
        "model": model,
        "stream": False,
        "messages": [{"role": "user", "content": message}]
    }, timeout=120.0)
    content = ""
    if isinstance(doc.get("message"), dict):
        content = str(doc["message"].get("content", ""))
    return {"model": model, "message": content, "done": bool(doc.get("done", False))}


def memory_candidate(summary: str, source_refs: list[str], tags: list[str]) -> dict:
    summary = summary.strip()
    if not summary or len(summary) > 4000:
        raise ValueError("summary length invalid")
    record = {
        "schema": "luhm.memoryCandidate.v1",
        "id": secrets.token_hex(12),
        "created_unix": int(time.time()),
        "state": "CANDIDATE_NOT_ACTIVE",
        "summary": summary,
        "source_refs": source_refs[:16],
        "tags": tags[:16],
        "promotion_authorized": False
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with MEMORY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n")
    return {"id": record["id"], "state": record["state"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models")
    p_chat = sub.add_parser("chat")
    p_chat.add_argument("model")
    p_chat.add_argument("message")
    p_mem = sub.add_parser("memory-candidate")
    p_mem.add_argument("summary")
    p_mem.add_argument("--source", action="append", default=[])
    p_mem.add_argument("--tag", action="append", default=[])
    args = parser.parse_args()
    if args.cmd == "models":
        result = {"models": models()}
    elif args.cmd == "chat":
        result = chat(args.model, args.message)
    else:
        result = memory_candidate(args.summary, args.source, args.tag)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
