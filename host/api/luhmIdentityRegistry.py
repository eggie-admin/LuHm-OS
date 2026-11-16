#!/usr/bin/env python3
"""LuHm CAST naming bridge: registry-locked 4×4 identity layers, no execution.

Independent Python interpretation of the JSON source used by the private npm
package. Does not read the live OS environment, execute an alias, or grant
authority based on a name, hexadecimal string or system-variable label.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "doctrine/castIdentityHexRegistryV1.json"
NAMING = ROOT / "doctrine/namingNamespaceCanonV1.json"
HELP = ROOT / "doctrine/commandHelpV1.json"
TYPED = ROOT / "doctrine/typedFourLaneSqlV1.json"
HOSTILE = ROOT / "doctrine/hostileModForge4x4V1.json"
LAYERS = ("camelHump", "vowelRipped", "shorthand", "utf8Hex")
LANES = ("numericStream", "textStream", "booleanStream", "aiManifestStream")
CANON = re.compile(r"[a-z][A-Za-z0-9]{0,79}\Z")
SHORT = re.compile(r"[a-z][a-z0-9]{0,11}\Z")
HEX = re.compile(r"(?:[0-9a-f]{2}){1,80}\Z")


def _load(path: Path) -> dict[str, Any]:
    x = json.loads(path.read_text(encoding="utf8"))
    if not isinstance(x, dict):
        raise ValueError("RED_IDENTITY_JSON")
    return x


def encode(name: str) -> str:
    if type(name) is not str or CANON.fullmatch(name) is None:
        raise ValueError("RED_IDENTITY_CANON")
    return name.encode("utf8").hex()


def decode(hex_name: str) -> str:
    if type(hex_name) is not str or HEX.fullmatch(hex_name) is None:
        raise ValueError("RED_IDENTITY_HEX")
    try:
        name = bytes.fromhex(hex_name).decode("utf8")
    except (ValueError, UnicodeError) as e:
        raise ValueError("RED_IDENTITY_HEX") from e
    if encode(name) != hex_name:
        raise ValueError("RED_IDENTITY_HEX")
    return name


def verified_registry() -> dict[str, Any]:
    r = _load(REGISTRY)
    if (r.get("schema") != "luhmOs.castIdentityHexRegistry.v1"
            or r.get("fourIdentityLayers") != list(LAYERS)
            or r.get("typedSqlLanes") != list(LANES)
            or r.get("tiers") != [0, 1, 2, 3]
            or r.get("crownStatus") != "STOP"):
        raise ValueError("RED_IDENTITY_REGISTRY_SCHEMA")
    policy = r.get("identityPolicy", {})
    for gate in ("singleCanonicalIdentity", "aliasRegistryIsExplicit",
                 "computedVowelAliasesNeverAcceptedAutomatically",
                 "allKindsCheckCollisionsAcrossEntries", "helpRecoversMeaning",
                 "noLossyReverseInference", "noAutoMigrateHistory"):
        if policy.get(gate) is not True:
            raise ValueError("RED_IDENTITY_REGISTRY_POLICY")
    if (policy.get("aliasMayGrantAuthority") is not False
            or policy.get("hexMayGrantAuthority") is not False
            or r.get("runtime", {}).get("activeWorkers") != 0
            or r.get("package", {}).get("private") is not True
            or r.get("package", {}).get("publishAuthorized") is not False):
        raise ValueError("RED_IDENTITY_REGISTRY_AUTHORITY")
    observed = _load(TYPED).get("lanes", [])
    if [x.get("id") for x in observed] != list(LANES):
        raise ValueError("RED_SQL_IDENTITY_LANES")
    aliases: dict[str, str] = {}
    records: dict[str, dict[str, Any]] = {}
    def register(alias: str, canonical: str) -> None:
        prior = aliases.get(alias)
        if prior is not None and prior != canonical:
            raise ValueError("RED_IDENTITY_ALIAS_COLLISION")
        aliases[alias] = canonical
    raw = r.get("bindings")
    if not isinstance(raw, list) or not 20 <= len(raw) <= 128:
        raise ValueError("RED_IDENTITY_BINDINGS")
    for row in raw:
        if not isinstance(row, dict):
            raise ValueError("RED_IDENTITY_BINDING_SHAPE")
        name = row.get("canonical")
        if (type(name) is not str or CANON.fullmatch(name) is None
                or type(row.get("vowelRipped")) is not str
                or CANON.fullmatch(row["vowelRipped"]) is None
                or type(row.get("shorthand")) is not str
                or SHORT.fullmatch(row["shorthand"]) is None
                or row.get("utf8Hex") != encode(name)
                or row.get("authority") != "IDENTITY_ONLY"
                or name in records):
            raise ValueError("RED_IDENTITY_BINDING_DRIFT")
        records[name] = row
        for alias in (name, row["vowelRipped"], row["shorthand"], row["utf8Hex"]):
            register(alias, name)
    for legacy in r.get("legacyAliases", []):
        if (not isinstance(legacy, dict)
                or type(legacy.get("alias")) is not str
                or CANON.fullmatch(legacy["alias"]) is None
                or legacy.get("canonical") not in records
                or legacy.get("authority") != "COMPATIBILITY_ONLY"):
            raise ValueError("RED_IDENTITY_LEGACY")
        register(legacy["alias"], legacy["canonical"])
    if _load(NAMING)["personCenteredDegradation"]["recoveryLaw"]["canonicalIdentityNeverDiscarded"] is not True:
        raise ValueError("RED_NAMING_SOURCE_DRIFT")
    for builtin in _load(HELP)["builtins"]:
        name = builtin["canonicalName"]
        if name not in records or any(
                records[name][key] != builtin["aliases"][alias_key]
                for key, alias_key in (("vowelRipped", "vowelRipped"), ("shorthand", "shorthand"))):
            raise ValueError("RED_HELP_SOURCE_ALIAS_DRIFT")
    env = _load(HOSTILE)["env"]["permitted"]
    if [b["name"] for b in r["systemVariableRegistry"]["bindings"]] != list(env):
        raise ValueError("RED_ENV_REGISTRY_DRIFT")
    return {"source": r, "byCanonical": records, "byAlias": aliases}


def resolve(alias: str) -> dict[str, Any]:
    if type(alias) is not str or len(alias) > 160:
        return {"status": "VERIFY", "canonical": None, "authority": False}
    registry = verified_registry()
    name = registry["byAlias"].get(alias)
    if name is None:
        return {"status": "VERIFY", "canonical": None, "authority": False}
    row = registry["byCanonical"][name]
    return {
        "status": "RESOLVED_IDENTITY_ONLY",
        "canonical": name, "vowelRipped": row["vowelRipped"],
        "shorthand": row["shorthand"], "utf8Hex": row["utf8Hex"],
        "humanMeaning": row["humanMeaning"],
        "authority": False, "executionAllowed": False,
    }


def cast_projection() -> dict[str, Any]:
    r = verified_registry()
    rows = r["byCanonical"]
    targets = ("professorLum", "lumMesh", *LANES)
    return {
        "schema": "luhmOs.castIdentityProjection.v1",
        "bindings": {k: {
            "canonical": k, "vowelRipped": rows[k]["vowelRipped"],
            "shorthand": rows[k]["shorthand"],
            "utf8Hex": rows[k]["utf8Hex"],
        } for k in targets},
        "matrix4x4": [{
            "typedLane": lane, "identityLayer": layer,
            "sourceOnly": True, "authority": False,
        } for lane in LANES for layer in LAYERS],
        "bindingCount": len(rows),
        "activeWorkers": 0,
        "registrySha256": hashlib.sha256(REGISTRY.read_bytes()).hexdigest(),
        "npmPublished": False,
        "sqlSourceChanged": False, "osVariablesChanged": False,
        "greenAuthority": False, "crownAuthority": False,
    }


if __name__ == "__main__":
    print(json.dumps(cast_projection(), indent=2))
