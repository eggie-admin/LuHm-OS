"""Reusable LuHm OS control-plane library, no privileged side effects.

Canonical entry point: LuHmOS.fn.operationTitan (build version 7).
A plan/diagnostic is not an execution receipt, deployment, authorization, or GREEN.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SHA = re.compile(r"^[0-9a-f]{40}$")
_TIERS = ("technologyFastPath", "forFuckSake", "scorchedEarth", "finalForm")
_OUTCOMES = ("working", "green", "blocked", "unknown", "conflict")
_MODES = ("system", "apply", "test", "all")


class LuHmOS:
    """Stable library namespace for typed LuHmOS functions."""

    class fn:
        """Functions resolve task envelopes without acquiring higher authority."""

        @staticmethod
        def operationTitan(*, mode: str, taskId: str, sourceRef: str,
                           actualSourceRef: str, scopeId: str,
                           milestoneId: str, tier: int = 0,
                           outcome: str = "working") -> dict:
            """Return a read-only Operation Titan v7 plan for one exact source.

            'apply' and 'all' stop at the unimplemented authorized mutation
            boundary. Callers must use separately approved executors and
            collect their own proof; this function never dispatches them.
            """
            execution = json.loads(
                (_ROOT / "doctrine/operationTitan7ExecutionSchemaV1.json").read_text(encoding="utf-8")
            )
            trigger = json.loads(
                (_ROOT / "doctrine/operationTitan7ChatTriggerV2.json").read_text(encoding="utf-8")
            )
            if execution.get("operationTitanFunctionRef") != "LuHmOS.fn.operationTitan":
                raise RuntimeError("TITAN_FUNCTION_BINDING_DRIFT")
            if trigger.get("buildVersion") != 7 or trigger.get("entryPoint") != "LuHmOS.fn.operationTitan":
                raise RuntimeError("TITAN_BUILD_BINDING_DRIFT")
            if mode not in _MODES or mode not in execution.get("modes", {}):
                raise ValueError("INVALID_TITAN_MODE")
            if type(tier) is not int or not 0 <= tier <= 3:
                raise ValueError("INVALID_TITAN_TIER")
            if outcome not in _OUTCOMES:
                raise ValueError("INVALID_TITAN_OUTCOME")
            for key, value in (("taskId", taskId), ("scopeId", scopeId),
                               ("milestoneId", milestoneId)):
                if not isinstance(value, str) or not value.strip() or len(value) > 128:
                    raise ValueError("INVALID_" + key)
            if not isinstance(sourceRef, str) or not _SHA.fullmatch(sourceRef):
                raise ValueError("INVALID_SOURCE_REF")
            if sourceRef != actualSourceRef:
                raise ValueError("SOURCE_REF_DRIFT")

            if outcome == "blocked":
                nextTier = min(3, tier + 1)
                decision = "ESCALATE" if tier < 3 else "HOLD_TIER_3_BLOCKER"
            elif outcome == "green":
                nextTier = max(0, tier - 1)
                decision = "CLOSE_OR_DEESCALATE"
            elif outcome in ("unknown", "conflict"):
                nextTier = tier
                decision = "HOLD_AND_DIAGNOSE"
            else:
                nextTier = tier
                decision = "CONTINUE_CURRENT_TIER"

            canPlanTests = mode in ("test", "all")
            requestedMutation = mode in ("apply", "all")
            return {
                "schema": "luhmOs.operationTitanPlan.v1",
                "functionRef": "LuHmOS.fn.operationTitan",
                "buildVersion": 7,
                "mode": mode,
                "taskId": taskId,
                "sourceRef": sourceRef,
                "scopeId": scopeId,
                "milestoneId": milestoneId,
                "currentTier": tier,
                "currentTierId": _TIERS[tier],
                "outcome": outcome.upper(),
                "decision": decision,
                "nextTier": nextTier,
                "nextTierId": _TIERS[nextTier],
                "testPlan": (
                    ["python3 tools/operationTitan7FinalFormAudit.py"]
                    if canPlanTests and tier == 3 else
                    ["python3 tools/escalationKernelAudit.py"] if canPlanTests else []
                ),
                "requestedMutation": requestedMutation,
                "mutationExecuted": False,
                "dispatch": "STOP_SEPARATE_AUTHORIZED_EXECUTOR" if requestedMutation else "NONE",
                "testsExecuted": False,
                "runtimeVerified": False,
                "greenClaim": False,
                "publicationAuthority": False,
                "mergeAuthority": False,
                "releaseAuthority": False,
                "crownStatus": "STOP",
                "operationBoundary": "READ_ONLY_PLAN",
            }
