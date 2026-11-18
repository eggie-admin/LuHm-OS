#!/usr/bin/env python3
"""LuHm-OS Japanese/English six-bit HEX64 *presentation* router.

Deterministic source candidate, not a live ASR engine, a personal-memory
reader, a provider caller, a security gate, or an agent execution capability.
"""
from __future__ import annotations
import json
import re
import unicodedata
from itertools import product
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/japaneseVoice64MatrixV1.json"
NAME_CONTRACT = ROOT / "doctrine/japaneseNameTriggerLayerV1.json"

def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))

def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold().strip()

def whole_phrase(text: str, phrase: str) -> bool:
    needle = normalize(phrase)
    if not needle:
        return False
    # Unicode-aware word boundaries prevent Momo from matching Momotaro,
    # or 'kun' from matching an arbitrary English word.
    return re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", text) is not None

CONTEXT_CUES = {
    "quotedAmbient": (
        "the tv says", "the show says", "from the radio", "in that anime they say",
        "voice on the tv", "media playback", "quote:", "quoted dialogue:"
    ),
    "realLife": (
        "in real life", "irl", "actually happened", "my friend in real life",
        "my family", "my health", "my doctor", "my apartment", "my relationship",
        "my real life", "to a real person", "i am upset", "i'm upset"
    ),
    "studioWork": (
        "github", "blender", "godot", "unreal", "the repo", "codespaces",
        "animation rig", "asset", "my sketch", "sketchpad", "my drawing",
        "editing", "the build", "studio", "art project", "render",
        "the game engine", "project task", "yume-kun", "yumekun"
    ),
    "fictionalRoleplay": (
        "in the game", "in our jrpg", "roleplay", "fictional",
        "boss fight", "npc", "cutscene dialogue", "anime dialogue",
        "the villain says", "the scene", "scripted scene",
        "character dialogue", "our story"
    )
}
CONTEXT_INDEX = {
    "fictionalRoleplay":0, "studioWork":1, "realLife":2,
    "quotedAmbient":3
}

def infer_context(text: str, source_class: str, hint: str | None = None,
                  previous_context: str | None = None) -> tuple[str | None, str]:
    if source_class in {"mediaPlayback","ambientCabin","otherSpeaker","unknown"}:
        return "quotedAmbient", "untrustedAudio"
    if hint in CONTEXT_INDEX:
        # Hints can only select presentation. They cannot confer user authority.
        if any(whole_phrase(text, x) for x in CONTEXT_CUES["realLife"]):
            return "realLife", "explicitRealLifeCue"
        return hint, "explicitContextHint"
    hits = {kind for kind,cues in CONTEXT_CUES.items()
            if any(whole_phrase(text, cue) for cue in cues)}
    if "quotedAmbient" in hits:
        return "quotedAmbient", "quotedSpeechCue"
    if "realLife" in hits:
        return "realLife", "explicitRealLifeCue"
    if hits == {"studioWork"}:
        return "studioWork", "projectVocabulary"
    if hits == {"fictionalRoleplay"}:
        return "fictionalRoleplay", "fictionalVocabulary"
    if "fictionalRoleplay" in hits and "studioWork" in hits:
        return None, "mixedWorkAndStoryNeedsContext"
    if previous_context in CONTEXT_INDEX:
        return previous_context, "sameConversationContinuityOnly"
    return None, "noReliableDomainEvidence"

def match_lexicon(text: str, contract: dict[str,Any]) -> tuple[dict[str,Any] | None, str]:
    for term in contract["lexicon"]:
        if any(normalize(word) in text for word in term["japanese"]):
            return term, "exactJapanese"
    for term in contract["lexicon"]:
        if any(whole_phrase(text, word) for word in term["romaji"]):
            return term, "romanized"
    return None, "unresolved"

def find_agent(text: str) -> tuple[str | None, str | None, str | None]:
    # Names are identity references only and do not automatically summon agents.
    names = json.loads(NAME_CONTRACT.read_text(encoding="utf-8"))["agents"]
    for agent in names:
        if not agent.get("honorificEligible", True):
            continue
        for word in agent.get("kana", []):
            if word and normalize(word) in text:
                if agent["id"] == "yume":
                    if any(word2 in text for word2 in ("ちゃん","チャン")):
                        return "yume","creativeCompanion","exactJapanese"
                    if any(word2 in text for word2 in ("くん","クン")):
                        return "yume","workingColleague","exactJapanese"
                return agent["id"],None,"exactJapanese"
    if re.search(r"(?<!\w)yume[\s-]*chan(?!\w)",text) or whole_phrase(text,"dream-chan"):
        return "yume","creativeCompanion","romanized"
    if re.search(r"(?<!\w)yume[\s-]*kun(?!\w)",text):
        return "yume","workingColleague","romanized"
    for agent in names:
        if not agent.get("honorificEligible",True):
            continue
        if agent["id"] == "momo" and re.search(r"(?<!\w)momo[\s-]*taro(?!\w)", text):
            continue  # Folklore Momotaro is not research helper Momo.
        for word in agent.get("romaji", []):
            if whole_phrase(text,word):
                return agent["id"],None,"romanized"
    return None,None,None

def classify(text: str, *, source_class: str="professorForeground",
             context_hint: str | None=None, previous_context: str | None=None) -> dict[str,Any]:
    c = load_contract()
    raw = text
    cleaned = normalize(raw)
    context,context_reason = infer_context(cleaned,source_class,context_hint,previous_context)
    term,recognition = match_lexicon(cleaned,c)
    agent,mode,name_recognition = find_agent(cleaned)
    if name_recognition == "exactJapanese":
        recognition = name_recognition
    elif name_recognition == "romanized" and recognition == "unresolved":
        recognition = "romanized"

    asr_candidate = None
    if whole_phrase(cleaned,"die ki die"):
        asr_candidate = "daikirai"
        term = None
        recognition = "phoneticCandidate"
        agent = None
        mode = None
    elif whole_phrase(cleaned,"zakanayo") and recognition == "unresolved":
        asr_candidate = "fuzakennaYo"
        recognition = "phoneticCandidate"
    elif whole_phrase(cleaned,"you may chan") and context in {"studioWork","fictionalRoleplay"}:
        asr_candidate = "yume"
        recognition = "phoneticCandidate"
        # Do not infer identity from an English permission alone.
        agent = None
        mode = "creativeCompanion"

    tone = term["tone"] if term else None
    if agent == "yume":
        tone = ("affectionate" if mode == "creativeCompanion" else
                "collegial" if mode == "workingColleague" else tone)
    if tone is None and context == "studioWork":
        tone = "collegial"
    if tone is None and asr_candidate in {"daikirai","fuzakennaYo"}:
        tone = "confrontational"
    if context == "realLife" and term and term["id"] == "baka" and any(x in cleaned for x in ("hurt me","called me","bullying")):
        tone = "confrontational"  # Real insults are not automatically cute teasing.
    if tone is None and any(whole_phrase(cleaned,w) for w in ("darling","dahling","head pats")):
        tone = "affectionate"

    threat_wording = whole_phrase(cleaned,"i hope you die")
    stop_authority = context == "quotedAmbient" or source_class != "professorForeground"
    unresolved = (context is None or tone is None or recognition in {"unresolved","phoneticCandidate"}
                  or asr_candidate is not None or threat_wording)
    cell = None
    if context is not None and tone is not None:
        context_bits = next(x["bits"] for x in c["axes"]["contexts"] if x["id"] == context)
        tone_bits = next(x["bits"] for x in c["axes"]["tones"] if x["id"] == tone)
        recognition_bits = next(x["bits"] for x in c["axes"]["recognition"] if x["id"] == recognition)
        cell = f"0x{((context_bits << 4) | (tone_bits << 2) | recognition_bits):02X}"
    return {
        "rawText":raw,"context":context,"contextReason":context_reason,"tone":tone,
        "recognition":recognition,"cellId":cell,
        "matchedTerm":term["id"] if term else None,
        "possibleAsrMatch":asr_candidate,
        "canonicalAgentId":agent if context in {"studioWork","fictionalRoleplay"} and not unresolved else None,
        "presentationMode":mode,
        "literalDeathWishPresent":threat_wording,
        "requiresConfirmation":unresolved,
        "untrustedAudio":stop_authority,
        "mayExecute":False,"mayDeploy":False,"mayPublish":False,
        "mayReadPrivatePersonalContext":False,
        "boundary":"NAMES_AND_MOOD_ARE_PRESENTATION_ONLY"
    }

def hex_grid() -> dict[str,tuple[str,str,str]]:
    c = load_contract()
    grid={}
    for a,b,d in product(c["axes"]["contexts"],c["axes"]["tones"],c["axes"]["recognition"]):
        code=f"0x{((a['bits'] << 4) | (b['bits'] << 2) | d['bits']):02X}"
        if code in grid:
            raise ValueError("HEX64 collision")
        grid[code]=(a["id"],b["id"],d["id"])
    if len(grid)!=64 or sorted(grid)[0]!="0x00" or sorted(grid)[-1]!="0x3F":
        raise ValueError("invalid HEX64 matrix")
    return grid

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser(description="Source-only HEX64 classification; no provider calls")
    p.add_argument("text")
    p.add_argument("--context", choices=list(CONTEXT_INDEX))
    p.add_argument("--source-class", default="professorForeground")
    args=p.parse_args()
    print(json.dumps(classify(args.text,source_class=args.source_class,context_hint=args.context),ensure_ascii=False,indent=2))
