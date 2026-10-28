"""SQL-first LuHm non-sensitive UI state lookup, candidate only.

No auto-connect, DDL, secret storage, network or publication. An approved runtime
passes an authenticated existing database connection. YAML is a reviewed safe
fallback. Markdown is never parsed for machine state.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SHA40 = re.compile(r"^[a-f0-9]{40}$")
NAMESPACE = "luhm"


class StateResolutionError(RuntimeError):
    pass


def readReviewedYaml(configPath: Path) -> dict[str, Any]:
    try:
        import yaml
        config = yaml.safe_load(configPath.read_text(encoding="utf-8"))
    except Exception as error:
        raise StateResolutionError("RED_YAML_CONFIG_UNAVAILABLE_OR_UNSAFE") from error
    if not isinstance(config, dict) or config.get("schema") != "luhmOs.statePrecedence.v1":
        raise StateResolutionError("RED_YAML_CONFIG_SCHEMA")
    if config.get("crownStatus") != "STOP" or config.get("rollout", {}).get("noProductionDdl") is not True:
        raise StateResolutionError("RED_YAML_CONFIG_AUTHORITY")
    return config


def reviewedDefault(config: dict[str, Any], stateKey: str) -> str:
    options = config.get("boundedKeys", {}).get(stateKey)
    if not isinstance(options, list) or not options or not all(isinstance(v, str) for v in options):
        raise StateResolutionError("RED_NON_WHITELISTED_KEY")
    component = stateKey.split(".")
    if len(component) != 2 or component[0] != "ui":
        raise StateResolutionError("RED_NOT_PUBLIC_UI_KEY")
    defaults = config.get("runtimeDefaults", {}).get(component[0], {})
    value = defaults.get(component[1]) if isinstance(defaults, dict) else None
    if value not in options:
        raise StateResolutionError("RED_YAML_DEFAULT_OUTSIDE_BOUNDS")
    return value


def resolveState(connection: Any | None, stateKey: str, configPath: Path,
                 sourceSha: str, *, backend: str = "mariadb",
                 allowOfflineUi: bool = False) -> dict[str, Any]:
    """Use an authorized SQL connection first; never silently escalate on an error.

    backend='sqlite' exists for in-memory unit tests, not as production topology.
    With no connection, only an explicitly flagged degraded UI can use YAML.
    """
    config = readReviewedYaml(configPath)
    fallback = reviewedDefault(config, stateKey)
    if not SHA40.fullmatch(sourceSha):
        raise StateResolutionError("RED_UNVERIFIED_SOURCE_SHA")
    if connection is None:
        if not allowOfflineUi:
            raise StateResolutionError("RED_EXISTING_DATABASE_REQUIRED")
        return {"value": fallback, "source": "yamlDefaults", "degraded": True}
    if backend not in ("sqlite", "mariadb"):
        raise StateResolutionError("RED_UNSUPPORTED_DATABASE_BACKEND")
    marker = "?" if backend == "sqlite" else "%s"
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT value_json, status, source_sha FROM luhm_runtime_state "
            f"WHERE namespace = {marker} AND state_key = {marker}",
            (NAMESPACE, stateKey),
        )
        row = cursor.fetchone()
    except Exception as error:
        if not allowOfflineUi:
            raise StateResolutionError("RED_DATABASE_QUERY_FAILED") from error
        return {"value": fallback, "source": "yamlDefaults", "degraded": True}
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
    if row is None:
        return {"value": fallback, "source": "yamlDefaults", "degraded": False}
    if not isinstance(row, (list, tuple)) or len(row) != 3:
        raise StateResolutionError("RED_DATABASE_ROW_SHAPE")
    packed, status, rowSha = row
    if status != "active":
        raise StateResolutionError("RED_DATABASE_ENTRY_REVOKED")
    if rowSha != sourceSha:
        raise StateResolutionError("RED_DATABASE_DOCTRINE_REVISION_CONFLICT")
    try:
        value = json.loads(packed)
    except (TypeError, ValueError) as error:
        raise StateResolutionError("RED_SQL_JSON_VALUE") from error
    if value not in config["boundedKeys"][stateKey] or not isinstance(value, str):
        raise StateResolutionError("RED_SQL_VALUE_OUTSIDE_BOUNDS")
    return {"value": value, "source": "sqlDatabase", "degraded": False}
