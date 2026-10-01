#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "doctrine" / "goddessTriad.json"
SCHEMA = ROOT / "doctrine" / "goddessTriad.schema.json"
SKILLS = {
    "urd": ROOT / "agents" / "urd" / "SKILL.md",
    "skuld": ROOT / "agents" / "skuld" / "SKILL.md",
    "belldandy": ROOT / "agents" / "belldandy" / "SKILL.md",
}

CAMEL_HUMP = re.compile(r"^[a-z][A-Za-z0-9]*$")
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
]

errors: list[str] = []
warnings: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load_json(path: Path, label: str) -> dict:
    require(path.is_file(), f"missing {label}: {path.relative_to(ROOT)}")
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid {label}: {exc}")
        return {}
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value if isinstance(value, dict) else {}


def check_camel_hump_keys(value: object, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if not key.startswith("$"):
                require(bool(CAMEL_HUMP.fullmatch(key)), f"non-camelHump key at {path}: {key}")
            check_camel_hump_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            check_camel_hump_keys(child, f"{path}[{index}]")


def check_grep_pattern(pattern: str, rule_id: str) -> None:
    try:
        result = subprocess.run(
            ["grep", "-E", pattern],
            input="",
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        warn("grep not available; regex syntax was not shell-validated")
        return
    require(result.returncode in (0, 1), f"invalid grep -E pattern for {rule_id}: {result.stderr.strip()}")


def assert_false_authority(obj: dict, label: str) -> None:
    for key in (
        "canMutate",
        "canBuild",
        "canMerge",
        "canPublish",
        "canDeploy",
        "canSign",
        "canCrown",
    ):
        require(obj.get(key) is False, f"{label}.{key} must be false")


def main() -> int:
    manifest = load_json(MANIFEST, "goddessTriad manifest")
    schema = load_json(SCHEMA, "goddessTriad schema")
    if errors:
        return finish()

    check_camel_hump_keys(manifest)

    require(schema.get("title") == "goddessTriad", "schema title must be goddessTriad")
    require(schema.get("type") == "object", "schema root must be object")
    require(schema.get("additionalProperties") is False, "schema root must fail closed on unknown fields")

    require(type(manifest.get("schemaVersion")) is int, "schemaVersion must be integer")
    require(manifest.get("schemaVersion") >= 1, "schemaVersion must be positive")
    require(manifest.get("systemId") == "goddessTriad", "systemId must be one-word camelHump goddessTriad")
    require(bool(CAMEL_HUMP.fullmatch(str(manifest.get("systemId", "")))), "systemId must be camelHump")
    require(manifest.get("displayName") == "Three Goddesses", "human display name drift")
    require(manifest.get("enabledByDefault") is True, "goddessTriad must default enabled")
    require(manifest.get("chatLoadMode") == "presenceAlwaysWorkOnDemand", "chat load mode drift")

    authority = manifest.get("authority", {})
    require(authority.get("professorIsCrown") is True, "Professor must remain Crown")
    require(authority.get("lumIsConversationalBoss") is True, "Lum must remain conversational boss")
    for key in (
        "selfCrown",
        "mergeAuthority",
        "publishAuthority",
        "deployAuthority",
        "signAuthority",
        "buildAuthorityWithoutCast",
    ):
        require(authority.get(key) is False, f"authority leak: {key}")

    goddesses = manifest.get("goddesses", {})
    require(set(goddesses) == {"urd", "skuld", "belldandy"}, "goddess set must be exactly urd/skuld/belldandy")

    expected_roles = {
        "urd": "truthGuard",
        "skuld": "librarianResearchArchitect",
        "belldandy": "secretaryStateKeeper",
    }
    expected_modes = {
        "urd": "passiveGuard",
        "skuld": "workOnDemand",
        "belldandy": "stateKeeper",
    }
    for name in ("urd", "skuld", "belldandy"):
        record = goddesses.get(name, {})
        require(record.get("id") == name, f"{name}.id drift")
        require(record.get("role") == expected_roles[name], f"{name}.role drift")
        require(record.get("workMode") == expected_modes[name], f"{name}.workMode drift")
        require(record.get("enabled") is True, f"{name} must be enabled")
        require(record.get("defaultPresence") is True, f"{name} must default present")
        require(isinstance(record.get("legacyAliases"), list), f"{name}.legacyAliases must be array")
        require(isinstance(record.get("activationPhrases"), list), f"{name}.activationPhrases must be array")
        assert_false_authority(record, name)
        require(SKILLS[name].is_file(), f"missing skill for {name}")

    require("Dr. Nao" in goddesses.get("urd", {}).get("legacyAliases", []), "Urd must preserve Dr. Nao alias")
    require("Secretary Oni" in goddesses.get("belldandy", {}).get("legacyAliases", []), "Belldandy must preserve Secretary Oni alias")

    commands = manifest.get("commands", {})
    require(commands.get("summonAll") == "summon the goddesses", "summon phrase drift")
    require(commands.get("takeBreak") == "goddesses take a break", "break phrase drift")
    require(commands.get("resumeAll") == "goddesses return", "resume phrase drift")

    limits = manifest.get("limits", {})
    for key in (
        "maxActiveGoddesses",
        "maxParallelResearchTasks",
        "maxAutomaticResearchQueries",
        "defaultEvidenceFreshnessHours",
        "maxReceiptRefsPerHandoff",
    ):
        require(type(limits.get(key)) is int, f"limits.{key} must be integer")
        require(limits.get(key, 0) > 0, f"limits.{key} must be positive")
    require(limits.get("maxActiveGoddesses") == 3, "exactly three active goddess slots required")
    require(limits.get("maxParallelResearchTasks") <= 3, "research parallelism may not exceed three")

    rules = manifest.get("grepRules", [])
    require(isinstance(rules, list) and len(rules) >= 3, "grepRules must contain multiple rules")
    for rule in rules:
        require(isinstance(rule, dict), "grep rule must be object")
        if not isinstance(rule, dict):
            continue
        rule_id = rule.get("id")
        require(isinstance(rule_id, str) and bool(CAMEL_HUMP.fullmatch(rule_id)), f"grep rule id must be camelHump: {rule_id}")
        require(rule.get("severity") in {"info", "amber", "red"}, f"invalid grep severity: {rule_id}")
        require(type(rule.get("enabled")) is bool, f"grep enabled must be boolean: {rule_id}")
        pattern = rule.get("pattern")
        require(isinstance(pattern, str) and bool(pattern), f"grep pattern required: {rule_id}")
        if isinstance(pattern, str) and pattern:
            check_grep_pattern(pattern, str(rule_id))

    skill_text = {name: path.read_text(encoding="utf-8") for name, path in SKILLS.items() if path.is_file()}
    require("No evidence -> no factual claim" in skill_text.get("urd", ""), "Urd did not inherit truth law")
    require("ENTERPRISE_DEFAULT_UNLESS_RED" in skill_text.get("urd", ""), "Urd enterprise-default guard missing")
    require("grep` is a locator, not proof" in skill_text.get("skuld", ""), "Skuld grep evidence boundary missing")
    require("Library dossier" in skill_text.get("skuld", ""), "Skuld library dossier missing")
    require("goddessTriad" in skill_text.get("belldandy", ""), "Belldandy chat bootstrap identity missing")
    require("ENTERPRISE_DEFAULT_UNLESS_RED" in skill_text.get("belldandy", ""), "Belldandy enterprise-default state tracking missing")

    all_candidate_text = "\n".join([
        MANIFEST.read_text(encoding="utf-8"),
        SCHEMA.read_text(encoding="utf-8"),
        *skill_text.values(),
    ])
    for pattern in SECRET_PATTERNS:
        require(pattern.search(all_candidate_text) is None, f"secret-like material matched: {pattern.pattern}")

    return finish()


def finish() -> int:
    if errors:
        print("GODDESS_TRIAD_AUDIT=RED")
        for error in errors:
            print(f"ERROR={error}")
        for item in warnings:
            print(f"WARNING={item}")
        print("crown=STOP")
        return 1

    print("GODDESS_TRIAD_AUDIT=GREEN")
    print("scope=static-chat-bootstrap-schema-and-skill-contract-only")
    print("systemId=goddessTriad")
    print("defaultPresence=urd,skuld,belldandy")
    print("buildAuthority=false")
    print("cast=NOT_ISSUED")
    print("crown=STOP")
    for item in warnings:
        print(f"WARNING={item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
