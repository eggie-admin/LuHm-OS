#!/usr/bin/env python3
"""LuHm GitHub-locked SQL source status and migration HOLD plans for MCP."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def register_github_sql_source_tools(server: Any, *, root: Path, annotations: Any) -> None:
    source = root / "tools/githubSqlSourceAudit.py"
    if not source.is_file():
        raise RuntimeError("RED_GITHUB_SQL_SOURCE_GATE_MISSING")
    spec = importlib.util.spec_from_file_location("githubSqlSourceAudit", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("RED_GITHUB_SQL_SOURCE_IMPORT")
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)

    @server.tool(
        name="luhm_sql_source_status",
        title="LuHm GitHub SQL source and migration safety status",
        description=(
            "Read Git-blob-locked SQL source manifest and verify three SQL files. "
            "SQLite STRICT schemas execute only in memory in this source audit; "
            "MariaDB remains static, disabled and unconnected. Never mutates a "
            "live database, repository branch, cloud VM or public API."
        ),
        annotations=annotations,
    )
    def luhm_sql_source_status() -> dict[str, Any]:
        return auditor.audit()

    @server.tool(
        name="luhm_sql_migration_plan",
        title="LuHm SQL proposed migration HOLD plan",
        description=(
            "For a bounded taskId, exact 40-hex sourceRef, scopeId, and one schemaId "
            "(fourLaneEvents, premonitionArt, mariaDbUpdateReceipts), return the "
            "required source, host and backup gates. This never executes SQL "
            "against any persistent database or grants release authority."
        ),
        annotations=annotations,
    )
    def luhm_sql_migration_plan(
        taskId: str, sourceRef: str, scopeId: str, schemaId: str
    ) -> dict[str, Any]:
        return auditor.plan(taskId, sourceRef, scopeId, schemaId)
