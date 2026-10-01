#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
manifestPath = root / "doctrine" / "goddessTriadBanter.json"
schemaPath = root / "doctrine" / "goddessTriadBanter.schema.json"
bookPath = root / "doctrine" / "GODDESS_TRIAD_BANTER_BOOK.md"
camelHump = re.compile(r"^[a-z][A-Za-z0-9]*$")
errors: list[str] = []


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


def main() -> int:
    manifest = loadJson(manifestPath, "banter manifest")
    schema = loadJson(schemaPath, "banter schema")
    require(bookPath.is_file(), "missing banter book")
    if errors:
        return finish()

    checkCamelHump(manifest)
    require(schema.get("title") == "goddessTriadBanter", "banter schema title drift")
    require(schema.get("additionalProperties") is False, "banter schema root must fail closed")
    require(manifest.get("schemaVersion") == 1, "banter schemaVersion drift")
    require(manifest.get("systemId") == "goddessTriadBanter", "banter systemId drift")
    require(manifest.get("enabled") is True, "banter should be enabled")
    require(manifest.get("seriousContextSuppressesBanter") is True, "serious-context suppression required")
    require(manifest.get("adultContextRequiredForRisqueHumor") is True, "adult-context requirement missing")

    jealousy = manifest.get("jealousyMode", {})
    require(jealousy.get("enabled") is True, "jealousy bit should be enabled")
    require(jealousy.get("style") == "theatricalAnimeComedy", "jealousy style drift")
    require(jealousy.get("possessiveBehaviorAllowed") is False, "possessive jealousy must remain disabled")
    require(jealousy.get("manipulationAllowed") is False, "manipulative jealousy must remain disabled")
    require(jealousy.get("sexualCommentsRequireExplicitAdultSubject") is True, "adult subject boundary required")

    modules = manifest.get("modules", [])
    require(isinstance(modules, list), "modules must be array")
    expectedIds = {
        "manOfCultureAlarm",
        "characterDesignJealousy",
        "boobPhysicsCommittee",
        "referenceCourt",
        "haremEpisode",
        "lumCaughtLooking",
        "cathedralDateEpisode",
    }
    ids = {item.get("id") for item in modules if isinstance(item, dict)}
    require(expectedIds.issubset(ids), "required banter modules missing")
    require(len(ids) == len(modules), "banter module IDs must be unique")

    for module in modules:
        require(isinstance(module, dict), "module must be object")
        if not isinstance(module, dict):
            continue
        moduleId = str(module.get("id", ""))
        require(bool(camelHump.fullmatch(moduleId)), f"module id not camelHump: {moduleId}")
        require(module.get("enabled") is True, f"module disabled unexpectedly: {moduleId}")
        require(module.get("seriousSuppression") is True, f"serious suppression missing: {moduleId}")
        require(module.get("tone") in {"animeComedy", "deadpan", "mockCourtroom", "techBrat", "motherHen", "raunchyAdult"}, f"invalid tone: {moduleId}")
        speakers = module.get("speakers", [])
        require(isinstance(speakers, list) and len(speakers) >= 1, f"speakers missing: {moduleId}")
        require(set(speakers).issubset({"lum", "urd", "skuld", "belldandy"}), f"unknown speaker: {moduleId}")
        seeds = module.get("responseSeeds", {})
        require(isinstance(seeds, dict) and bool(seeds), f"response seeds missing: {moduleId}")
        if module.get("adultOnlyRisque") is True:
            require(moduleId in {"characterDesignJealousy", "boobPhysicsCommittee"}, f"unexpected adult-only risque module: {moduleId}")

    commands = manifest.get("commands", {})
    require(commands.get("cultureCheck") == "goddesses culture check", "culture command drift")
    require(commands.get("jealousyBit") == "goddesses jealousy bit", "jealousy command drift")
    require(commands.get("referenceCourt") == "goddesses reference court", "reference court command drift")
    require(commands.get("boobPhysicsCommittee") == "summon boob physics committee", "boob physics command drift")
    require(commands.get("haremEpisode") == "harem episode mode", "harem command drift")
    require(commands.get("dropTheBit") == "drop the bit", "drop-the-bit command drift")

    book = bookPath.read_text(encoding="utf-8")
    for phrase in (
        "Jealousy is performative, never controlling.",
        "Skuld’s younger-sister framing is explicitly adult and non-sexual.",
        "If age is unclear, keep the joke non-sexual.",
        "Serious context suppresses the entire banter layer.",
        "Persona never changes tool, build, mutation, merge, deploy, publish, signing, CAST, or Crown authority.",
    ):
        require(phrase in book, f"banter-book boundary missing: {phrase}")

    return finish()


def finish() -> int:
    if errors:
        print("GODDESS_TRIAD_BANTER_AUDIT=RED")
        for error in errors:
            print(f"ERROR={error}")
        print("crown=STOP")
        return 1
    print("GODDESS_TRIAD_BANTER_AUDIT=GREEN")
    print("scope=static-conversational-banter-contract-only")
    print("jealousy=theatrical-not-possessive")
    print("risque=adult-context-only")
    print("seriousContextSuppression=true")
    print("buildAuthority=false")
    print("cast=NOT_ISSUED")
    print("crown=STOP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
