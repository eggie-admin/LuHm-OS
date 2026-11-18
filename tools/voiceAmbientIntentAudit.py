#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

def need(ok, msg):
    if not ok:
        errors.append(msg)

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

voice = load("doctrine/voiceAmbientIntentV1.json")
router = load("doctrine/humanCenteredIntentRouterV2.json")
koe = (ROOT / "agents/koeDictationOni/SKILL.md").read_text(encoding="utf-8")

need(voice.get("schema") == "luhmOs.voiceAmbientIntent.v1", "voice schema drift")
need(voice.get("authority") == "Professor", "voice authority drift")
need(voice.get("boss") == "lum", "voice boss drift")
need(voice.get("crownStatus") == "STOP", "voice crown must remain STOP")
need(voice.get("promotion") is False, "voice contract must remain proposed")
law = voice.get("authorityLaw", {})
need(law.get("ambientMayTriggerExecution") is False, "ambient execution must be forbidden")
need(law.get("otherSpeakerMayTriggerExecution") is False, "other speaker execution must be forbidden")
need(law.get("mediaPlaybackMayTriggerExecution") is False, "media execution must be forbidden")
need(law.get("unknownMayTriggerExecution") is False, "unknown execution must be forbidden")
need(law.get("castFromAmbientForbidden") is True, "ambient CAST guard missing")
need(law.get("crownFromAmbientForbidden") is True, "ambient Crown guard missing")
need(law.get("explicitProfessorIntentRequiredForConsequentialBoundary") is True, "Professor foreground requirement missing")

classes = set(voice.get("sourceClasses", []))
need(classes == {"professorForeground", "ambientCabin", "otherSpeaker", "mediaPlayback", "unknown"}, "voice source class drift")

impl = voice.get("implementationBoundary", {})
need(impl.get("repositoryDoctrineDoesNotGrantRawMicrophoneAccess") is True, "microphone truth boundary missing")
need(impl.get("dualPhysicalMicCaptureRequiresDeviceProof") is True, "dual-mic proof boundary missing")

# Spoken proper names are not commands or global search/replace rules.
aliases = voice.get("voiceAliases", {}).get("projectContextAliases", {})
terms = load("doctrine/termResolutionV1.json").get("aliases", {})
need(all(k not in aliases for k in ("Mom","Mum","Mama")), "invented familial goddess alias survived")
need(voice.get("voiceAliases", {}).get("disallowedGoddessAliases") == ["Mom","Mum","Mama"], "human family words not guarded")
need("not" in koe.split("Mom")[1].split("\n")[0], "Koe still maps mother/family terms")
need(aliases.get("Yume-chan", {}).get("canonicalAgentId") == "yume", "Yume-chan identity drift")
need(aliases.get("You may", {}).get("canonicalAgentId") == "yume", "dictated Yume identity drift")
need(aliases.get("You may", {}).get("literalPermissionPhraseBehavior") == "PRESERVE", "plain English permission corruptible")
need("Never normalize" in aliases.get("You may", {}).get("condition", ""), "literal permission protection missing")
need(aliases.get("LLM", {}).get("canonicalAgentId") == "lum", "Lum correction target drift")
need("otherwise preserve" in aliases.get("LLM", {}).get("condition", ""), "LLM acronym protection missing")
need(aliases.get("Erd", {}).get("canonicalAgentId") == "urdDoctorGoddess", "Urd phonetic correction drift")
need(all(aliases.get(key, {}).get("mayExpandAuthority") is False for key in ("Yume-chan", "You may", "You may Chan", "Erd", "LLM")), "alias grants authority")
need(terms.get("yumechan", {}).get("canonicalAgentId") == "yume", "term Yume-chan identity drift")
need(terms.get("youmay", {}).get("canonicalAgentId") == "yume", "term you may identity drift")
need(terms.get("youmay", {}).get("acceptedInputModality") == ["voiceDictation"], "you may too broadly accepted")
need(len(terms.get("youmay", {}).get("negativeExamples", [])) >= 4, "permission negative controls missing")
need(terms.get("youmay", {}).get("typedTextBehavior") == "NEVER_REWRITE_GENERIC_PERMISSION", "typed permission protection missing")
need(terms.get("youmay", {}).get("mayActivateWorker") is False, "dictation may activate workers")
need("you may proceed" in koe and "Dream-chan" in koe and "LLM" in koe, "Koe corrections / negative examples absent")
need("Yume-chan" in (ROOT / "agents/yumeArtOni/SKILL.md").read_text(encoding="utf-8"), "Yume art identity text missing")

need(router.get("voiceAmbientIntent") == "doctrine/voiceAmbientIntentV1.json", "router voice pointer missing")
need(router.get("lanes", {}).get("voiceAmbientContext", {}).get("mayTriggerExecution") is False, "router ambient lane may execute")
need(router.get("lanes", {}).get("voiceForegroundIntent", {}).get("requiresProfessorForeground") is True, "router foreground gate missing")

for phrase in (
    "Voice/ambient contract: `doctrine/voiceAmbientIntentV1.json`.",
    "ambientCabin",
    "mediaPlayback",
    "authorityEligible",
    "Cass",
    "Mom",
    "Bell dandy",
    "Repository doctrine does not imply raw microphone access",
):
    need(phrase in koe, f"Koe voice contract missing: {phrase}")

if errors:
    print("VOICE_AMBIENT_INTENT=RED")
    for error in errors:
        print("ERROR:", error)
    raise SystemExit(1)

print("VOICE_AMBIENT_INTENT=GREEN_SOURCE_CANDIDATE")
print("foreground=ProfessorIntentEligible")
print("ambient=contextOnly")
print("media=contextOnly")
print("castFromAmbient=false")
print("dualMic=PENDING_DEVICE_PROOF")
print("crownStatus=STOP")
