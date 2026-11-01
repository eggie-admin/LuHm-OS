"""Read-only creative source registry tools."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Any

def register_creative_module_forge(server: Any, *, root: Path, annotations: Any) -> None:
    path = root / "tools" / "creativeCommunityAudit.py"
    spec = importlib.util.spec_from_file_location("creativeCommunityAudit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("CREATIVE_SOURCE_IMPORT")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    @server.tool(name="luhm_creative_module_status",
                 title="LuHm RPG four-lane source status",
                 description="Read Git-backed RPG, RSS and art pipeline source candidate status.",
                 annotations=annotations)
    def luhm_creative_module_status() -> dict[str, Any]:
        return m.audit()

    @server.tool(name="luhm_creative_source_plan",
                 title="LuHm original RPG external reference plan",
                 description="Read-only source metadata and per-file license review plan.",
                 annotations=annotations)
    def luhm_creative_source_plan(taskId: str, sourceRef: str, scopeId: str,
                                 referenceId: str, claimedLicense: str) -> dict[str, Any]:
        return m.candidate(task_id=taskId, source_ref=sourceRef,
                           scope_id=scopeId, reference_id=referenceId,
                           asset_license=claimedLicense)
