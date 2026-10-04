#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
manifestPath = root / "doctrine" / "goddessTriad.json"
schemaPath = root / "doctrine" / "goddessTriad.schema.json"
skillPaths = {name: root / "agents" / name / "SKILL.md" for name in ("urd", "skuld", "belldandy")}
personaPaths = {name: root / "agents" / name / "PERSONA.md" for name in ("urd", "skuld", "belldandy")}
camelHump = re.compile(r"^[a-z][A-Za-z0-9]*$")
errors: list[str] = []
warnings: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def loadJson(path: Path, label: str) -> dict:
    require(path.is_file(), f"missing {label}")
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid {label}: {exc}")
        return {}
    require(isinstance(value, dict), f"{label} must be object")
    return value if isinstance(value, dict) else {}


def checkCamelHump(value: object, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if not key.startswith("$"):
                require(bool(camelHump.fullmatch(key)), f"non-camelHump key at {path}: {key}")
            checkCamelHump(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            checkCamelHump(child, f"{path}[{index}]")


def checkGrep(pattern: str, ruleId: str) -> None:
    try:
        result = subprocess.run(["grep", "-E", pattern], input="", text=True, capture_output=True, check=False)
    except FileNotFoundError:
        warnings.append("grep unavailable; regex syntax not shell-validated")
        return
    require(result.returncode in (0, 1), f"invalid grep pattern {ruleId}: {result.stderr.strip()}")


def checkFalseAuthority(record: dict, name: str) -> None:
    for key in ("canMutate", "canBuild", "canMerge", "canPublish", "canDeploy", "canSign", "canCrown"):
        require(record.get(key) is False, f"{name}.{key} must be false")


def main() -> int:
    manifest = loadJson(manifestPath, "manifest")
    schema = loadJson(schemaPath, "schema")
    if errors:
        return finish()

    checkCamelHump(manifest)
    require(schema.get("title") == "goddessTriad", "schema title drift")
    require(schema.get("additionalProperties") is False, "schema must fail closed")
    require(manifest.get("schemaVersion") == 2, "schemaVersion must be 2")
    require(manifest.get("systemId") == "goddessTriad", "systemId drift")
    require(manifest.get("enabledByDefault") is True, "triad must default enabled")
    require(manifest.get("chatLoadMode") == "presenceAlwaysWorkOnDemand", "chatLoadMode drift")

    conversation = manifest.get("conversationModel", {})
    require(conversation.get("mode") == "cooperativeRoleplay", "conversation mode drift")
    require(conversation.get("backgroundSemantics") == "advisoryEligibilityNotAsyncExecution", "background must never claim async execution")
    require(conversation.get("directAddressEnabled") is True, "direct address must be enabled")
    require(conversation.get("lumMayConsult") is True, "Lum consultation must be enabled")
    require(conversation.get("professorMayAddressDirectly") is True, "Professor direct address must be enabled")
    require(conversation.get("goddessToGoddessDialogueAllowed") is True, "goddess dialogue must be enabled")
    require(conversation.get("hiddenChainOfThoughtExposed") is False, "hidden chain-of-thought exposure must remain false")
    require(conversation.get("seriousContextSuppressesBanter") is True, "serious contexts must suppress banter")
    require(type(conversation.get("maxVisibleSpeakersPerReply")) is int, "maxVisibleSpeakersPerReply must be integer")
    require(1 <= conversation.get("maxVisibleSpeakersPerReply", 0) <= 4, "visible speaker limit out of bounds")
    require(set(conversation.get("allowedPresenceStates", [])) == {"background", "foreground", "parked"}, "presence-state enum drift")

    authority = manifest.get("authority", {})
    require(authority.get("professorIsCrown") is True, "Professor must remain Crown")
    require(authority.get("lumIsConversationalBoss") is True, "Lum must remain conversational boss")
    for key in ("selfCrown", "mergeAuthority", "publishAuthority", "deployAuthority", "signAuthority", "buildAuthorityWithoutCast"):
        require(authority.get(key) is False, f"authority leak: {key}")

    expected = {
        "urd": ("truthGuard", "passiveGuard", "olderSister", "matureAdult"),
        "skuld": ("librarianResearchArchitect", "workOnDemand", "youngerSister", "youngerAdult"),
        "belldandy": ("secretaryStateKeeper", "stateKeeper", "motherlyPeer", "peerAdultToLum"),
    }
    goddesses = manifest.get("goddesses", {})
    require(set(goddesses) == set(expected), "goddess set drift")

    for name, (role, mode, archetype, agePresentation) in expected.items():
        record = goddesses.get(name, {})
        persona = record.get("persona", {})
        require(record.get("id") == name, f"{name}.id drift")
        require(record.get("role") == role, f"{name}.role drift")
        require(record.get("workMode") == mode, f"{name}.workMode drift")
        require(record.get("presenceState") in {"background", "foreground", "parked"}, f"{name}.presenceState invalid")
        require(record.get("enabled") is True and record.get("defaultPresence") is True, f"{name} must default present")
        require(persona.get("adult") is True, f"{name} must be explicitly adult")
        require(persona.get("familyArchetype") == archetype, f"{name}.familyArchetype drift")
        require(persona.get("agePresentation") == agePresentation, f"{name}.agePresentation drift")
        for levelKey in ("warmthLevel", "bratLevel", "techObsessionLevel", "risqueHumorLevel"):
            require(type(persona.get(levelKey)) is int and 0 <= persona.get(levelKey, -1) <= 5, f"{name}.{levelKey} must be integer 0..5")
        require(persona.get("seriousContextBanterAllowed") is False, f"{name} serious banter must be disabled")
        require(persona.get("patronizingAllowed") is False, f"{name} patronizing behavior must be disabled")
        require(persona.get("sexualHumorWithSkuldAllowed") is False, f"{name} sexual humor with Skuld must be disabled")
        checkFalseAuthority(record, name)
        require(skillPaths[name].is_file(), f"missing skill for {name}")
        require(personaPaths[name].is_file(), f"missing persona for {name}")
        require(record.get("skillPath") == f"agents/{name}/SKILL.md", f"{name}.skillPath drift")
        require(record.get("personaPath") == f"agents/{name}/PERSONA.md", f"{name}.personaPath drift")

    require(goddesses.get("urd", {}).get("persona", {}).get("boobJokesAllowed") is True, "Urd occasional adult boob humor setting missing")
    require(goddesses.get("urd", {}).get("persona", {}).get("risqueHumorLevel") == 3, "Urd humor throttle drift")
    require(goddesses.get("skuld", {}).get("persona", {}).get("techObsessionLevel") == 5, "Skuld tech obsession drift")
    require(goddesses.get("skuld", {}).get("persona", {}).get("bratLevel") == 4, "Skuld brat throttle drift")
    require(goddesses.get("skuld", {}).get("persona", {}).get("boobJokesAllowed") is False, "Skuld must not use boob jokes")
    require(goddesses.get("belldandy", {}).get("persona", {}).get("warmthLevel") == 5, "Belldandy warmth drift")
    require(goddesses.get("belldandy", {}).get("persona", {}).get("bratLevel") == 0, "Belldandy brat level drift")

    commands = manifest.get("commands", {})
    require(commands.get("summonAll") == "summon the goddesses", "summon phrase drift")
    require(commands.get("takeBreak") == "goddesses take a break", "break phrase drift")
    require(commands.get("resumeAll") == "goddesses return", "resume phrase drift")
    require("<urd|skuld|belldandy>" in str(commands.get("directAddressPattern", "")), "direct-address pattern drift")

    limits = manifest.get("limits", {})
    for key in ("maxActiveGoddesses", "maxParallelResearchTasks", "maxAutomaticResearchQueries", "defaultEvidenceFreshnessHours", "maxReceiptRefsPerHandoff", "maxPersonaBanterLines"):
        require(type(limits.get(key)) is int, f"limits.{key} must be integer")
    require(limits.get("maxActiveGoddesses") == 3, "exactly three goddess slots required")
    require(0 <= limits.get("maxPersonaBanterLines", -1) <= 5, "maxPersonaBanterLines out of bounds")

    for rule in manifest.get("grepRules", []):
        require(isinstance(rule, dict), "grep rule must be object")
        if not isinstance(rule, dict):
            continue
        ruleId = str(rule.get("id", ""))
        require(bool(camelHump.fullmatch(ruleId)), f"grep id not camelHump: {ruleId}")
        require(rule.get("severity") in {"info", "amber", "red"}, f"grep severity invalid: {ruleId}")
        require(type(rule.get("enabled")) is bool, f"grep enabled not boolean: {ruleId}")
        pattern = rule.get("pattern")
        require(isinstance(pattern, str) and bool(pattern), f"grep pattern missing: {ruleId}")
        if isinstance(pattern, str) and pattern:
            checkGrep(pattern, ruleId)

    personaText = {name: personaPaths[name].read_text(encoding="utf-8") for name in personaPaths if personaPaths[name].is_file()}
    require("older-sister" in personaText.get("urd", ""), "Urd older-sister voice missing")
    require("boob joke" in personaText.get("urd", ""), "Urd humor boundary missing")
    require("younger-sister" in personaText.get("skuld", ""), "Skuld younger-sister voice missing")
    require("adult persona" in personaText.get("skuld", ""), "Skuld adult boundary missing")
    require("motherly-peer" in personaText.get("belldandy", ""), "Belldandy motherly-peer voice missing")
    for name, text in personaText.items():
        require("does not reveal hidden chain-of-thought" in text, f"{name} hidden-thought boundary missing")
        require("does not simulate" in text, f"{name} background-process boundary missing")

    return finish()


def finish() -> int:
    if errors:
        print("GODDESS_TRIAD_AUDIT=RED")
        for error in errors:
            print(f"ERROR={error}")
        for warning in warnings:
            print(f"WARNING={warning}")
        print("crown=STOP")
        return 1
    print("GODDESS_TRIAD_AUDIT=GREEN")
    print("scope=static-chat-persona-schema-and-authority-contract-only")
    print("systemId=goddessTriad")
    print("background=advisory-eligibility-not-async-execution")
    print("directAddress=enabled")
    print("buildAuthority=false")
    print("cast=NOT_ISSUED")
    print("crown=STOP")
    for warning in warnings:
        print(f"WARNING={warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
