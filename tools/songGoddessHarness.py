"""Song of the Goddess: bounded, source-only four-lane harness."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
import re

LANES = ("canon", "implementation", "sidecar", "reconciliation")
BEATS = ("inspect", "plan", "test", "verify")
STATUSES = ("NULL", "GREEN", "AMBER", "RED", "BLOCKED")

@dataclass(frozen=True)
class Check:
    lane: str
    beat: str
    status: str
    evidence: str = ""
    reason: str = ""

    def __post_init__(self):
        if self.lane not in LANES or self.beat not in BEATS or self.status not in STATUSES:
            raise ValueError("unknown lane, beat or status")
        if self.status == "GREEN" and not self.evidence:
            raise ValueError("GREEN requires evidence")

def receipt(source_ref, rows, source_stable):
    counts = {s: sum(r["status"] == s for r in rows) for s in STATUSES}
    status = ("RED" if counts["RED"] else "AMBER" if
              not source_stable or len(rows) != 16 or
              any(counts[s] for s in ("NULL", "AMBER", "BLOCKED")) else "GREEN")
    body = {"schema": "luhmOs.songGoddessHarness.v1", "sourceRef": source_ref,
            "sourceStable": source_stable, "checks": rows, "counts": counts,
            "sourceAuditStatus": status, "executionAuthority": False,
            "promotionAuthority": False, "crownStatus": "STOP"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    body["receiptSha256"] = sha256(encoded.encode("utf-8")).hexdigest()
    return body

def four_loop(source_ref, checks, *, source_now, max_checks=16):
    """Run registered checks only; failures stop their lane, not other lanes."""
    if not re.fullmatch(r"[0-9a-f]{40}", source_ref):
        raise ValueError("exact lowercase SHA required")
    if not 0 <= max_checks <= 16:
        raise ValueError("outside 4x4 budget")
    rows = []
    for lane in LANES:
        for beat in BEATS:
            if len(rows) >= max_checks:
                break
            if source_now() != source_ref:
                return receipt(source_ref, rows, False)
            fn = checks.get((lane, beat))
            if fn is None:
                rows.append(Check(lane, beat, "NULL", reason="unregistered").__dict__)
                break
            try:
                check = fn()
                if not isinstance(check, Check) or (check.lane, check.beat) != (lane, beat):
                    raise ValueError("check identity mismatch")
            except Exception as exc:
                check = Check(lane, beat, "RED", reason=type(exc).__name__)
            rows.append(check.__dict__)
            if check.status != "GREEN":
                break
    return receipt(source_ref, rows, source_now() == source_ref)

def netplan_like_plan(current, desired):
    """Pure inspect/diff plan. Never runs netplan, applies config or opens ports."""
    if not isinstance(current, dict) or not isinstance(desired, dict):
        raise TypeError("mapping inputs required")
    changes = [{"key": k, "before": current.get(k), "after": desired.get(k)}
               for k in sorted(set(current) | set(desired))
               if current.get(k) != desired.get(k)]
    return {"status": "PROPOSED", "changes": changes,
            "applyExecuted": False, "rollbackRequired": bool(changes),
            "authority": "NONE"}
