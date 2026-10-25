#!/usr/bin/env python3
"""Read-only Old Magic speech adapter. Never dispatch tools or infer owner authorization.

This is a deterministic convenience classifier, NOT a large language model,
not persistent memory, and not an authority token. Output omits raw user text.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "oldMagicSpeechV1.json"

_OOC = re.compile(r"\b(?:out[ -]of[ -]character|ooc|irl)\b", re.I)
_IC = re.compile(r"\b(?:in[ -]character|in[ -]scene|after[ -]hours)\b", re.I)
_WORDS = {
    "blessing": re.compile(r"\b(?:bless|blessing|crown|supreme goddess)\b", re.I),
    "mythology": re.compile(r"\b(?:old magic|warp|alignment|chaotic good|spellbook|altar|way(?:s)? of war)\b", re.I),
    "evidence": re.compile(r"\b(?:build status|build passed|ci|tests? passed|audit result|proof|runtime|deployment status)\b", re.I),
    "task": re.compile(r"\b(?:please (?:implement|build|fix|check|review)|(?:implement|fix|audit) (?:the|our|this)|can you (?:build|implement|fix|check))\b", re.I),
}
_CAST_EXACT = re.compile(r"^\s*(?:CAST|castBridge|/cast(?:\s+[A-Za-z][\w-]{1,96})?)\s*$", re.I)
_SAFE_TEXT_LIMIT = 4000


def interpret(message: str) -> dict:
    if not isinstance(message, str) or len(message) > _SAFE_TEXT_LIMIT:
        raise ValueError("TEXT_INVALID_OR_TOO_LONG")
    text = message.strip()
    if not text:
        raise ValueError("TEXT_EMPTY")

    # Explicit OOC wins over poetic words in the very same turn.
    # If both are present, the final explicit mode cue decides that turn.
    # Embedded references to modes are just a conservative approximation.
    cues = [(m.start(), "outOfCharacter") for m in _OOC.finditer(text)]
    cues += [(m.start(), "inCharacter") for m in _IC.finditer(text)]
    mode = sorted(cues)[-1][1] if cues else "normal"
    blessing = bool(_WORDS["blessing"].search(text))
    mythology = bool(_WORDS["mythology"].search(text))
    exact_cast = bool(_CAST_EXACT.fullmatch(text))

    if exact_cast:
        intent = "requestCastReview"
        review = "EXISTING_PROFESSOR_CAST_GATE_REQUIRED"
    elif _WORDS["evidence"].search(text):
        intent = "reviewBuildEvidence"
        review = "FETCH_CURRENT_EXACT_SOURCE_PROOF"
    elif _WORDS["task"].search(text) and not blessing:
        intent = "ordinaryTask"
        review = "NORMAL_TOOL_APPROVAL_AND_SCOPE"
    elif blessing and (mode == "inCharacter" or mythology):
        intent = "fictionalBlessing" if mode == "inCharacter" else "socialAcknowledgement"
        review = "NONE"
    else:
        intent = "socialAcknowledgement"
        review = "NONE"

    return {
        "schema": "luhmOs.oldMagicSpeechInterpretation.v1",
        "mode": mode,
        "intent": intent,
        "alignment": "chaoticGood",
        "color": "blue",
        "blessingIsAuthority": False,
        "theatricalCastDispatch": False,
        "privilegedEffect": False,
        "needsReview": review,
        "sourceReferenceRequiredForBuild": exact_cast,
        "hasMythicVocabulary": mythology,
        "speechStored": False,
        "deploymentAuthorized": False,
        "crown": "STOP",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True, help="Only classified in memory; not printed to output.")
    args = parser.parse_args()
    doctrine = json.loads(DOCTRINE.read_text(encoding="utf-8"))
    if doctrine.get("schema") != "luhmOs.oldMagicSpeech.v1":
        raise SystemExit("OLD_MAGIC_DOCTRINE_MISMATCH")
    print(json.dumps(interpret(args.text), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
