#!/usr/bin/env python3
"""LuHm-OS: Project Premonition 500 source controls. No runtime GREEN implied."""
import argparse
import ast
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "ca369e6925406e9a00008bbc629bb5db67a7d02c"
HARD_RE = re.compile(r"^(PASS|FAIL) (\d{3})/200 (\S+)$")

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="build/premonition-cast-receipts")
    args = parser.parse_args()
    canon = load("doctrine/premonitionCathedralCastV1.json")
    inventory = load("doctrine/premonition-titan-500-inventory-v1.json")
    assert canon["displayIdentity"] == "LuHm-OS: Project Premonition"
    assert canon["caseSensitiveBrand"] is True
    assert canon["crownStatus"] == "STOP"
    assert inventory["count"] == len(inventory["checks"]) == 180
    assert len({x["path"] for x in inventory["checks"]}) == 180
    assert len({x["id"] for x in inventory["checks"]}) == 180
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    results = []
    env = dict(os.environ, LUHM_SOURCE_REF=source)
    hard = subprocess.run([sys.executable, "tools/hardSystemAudit200.py"], cwd=ROOT, env=env, text=True, capture_output=True)
    (output / "hard-system-200.log").write_text(hard.stdout + "\n" + hard.stderr, encoding="utf-8")
    hard_rows = {}
    for line in hard.stdout.splitlines():
        match = HARD_RE.match(line)
        if match:
            status, index, label = match.groups()
            hard_rows[int(index)] = (status, label)
    for index in range(1, 201):
        state, label = hard_rows.get(index, ("UNVERIFIED", "Audit output missing"))
        results.append({"id": f"hard-{index:03d}", "domain": "hardSystem", "label": label,
                        "result": state, "proofClass": "source", "detail": "Existing 200-control audit"})
    with tempfile.TemporaryDirectory() as tmp:
        art = subprocess.run([sys.executable, "tools/artist-first-canon-audit.py", "--output-dir", tmp],
                             cwd=ROOT, text=True, capture_output=True)
        (output / "artist-first-120.log").write_text(art.stdout + "\n" + art.stderr, encoding="utf-8")
        receipt = Path(tmp) / "artist-first-120-receipt.json"
        rows = json.loads(receipt.read_text())["checks"] if receipt.exists() else []
        if rows and len(rows) != 120:
            raise SystemExit("RED_ARTIST_AUDIT_COUNT_DRIFT")
        for index in range(120):
            row = rows[index] if index < len(rows) else {}
            results.append({"id": f"artist-{index+1:03d}", "domain": row.get("domain", "artist"),
                            "label": row.get("label", "Missing audit receipt"),
                            "result": row.get("result", "UNVERIFIED"),
                            "proofClass": "runtime" if row.get("kind") == "runtime" else "source",
                            "critical": row.get("critical", False), "detail": row.get("evidence", "No receipt")})
    for row in inventory["checks"]:
        target = ROOT / row["path"]
        valid = target.is_file() and target.resolve().is_relative_to(ROOT)
        digest = None
        if valid:
            try:
                data = target.read_bytes()
                if not data:
                    valid = False
                elif row["kind"] == "json-syntax":
                    json.loads(data.decode("utf-8"))
                elif row["kind"] == "python-syntax":
                    ast.parse(data.decode("utf-8"), filename=row["path"])
                if valid:
                    digest = hashlib.sha256(data).hexdigest()
            except (ValueError, UnicodeError, SyntaxError, OSError):
                valid = False
        results.append({"id": row["id"], "domain": row["domain"], "label": row["path"],
                        "result": "PASS" if valid else "GAP", "proofClass": "sourceInventory",
                        "detail": {"path": row["path"], "sha256": digest}})
    if len(results) != 500 or len({r["id"] for r in results}) != 500:
        raise SystemExit("RED_TITAN500_AUDIT_COUNT")
    # Distinguish critical source regressions from openly documented feature gaps.
    # No unresolved gap is counted as a PASS or as runtime readiness.
    source_blockers = [
        r["id"] for r in results
        if (r["id"].startswith("hard-") or r["id"].startswith("inventory-")
            or (r["id"].startswith("artist-") and r.get("critical", False)))
        and r["result"] != "PASS"
    ]
    if hard.returncode != 0:
        source_blockers.append("hardSystemProcessExit")
    if art.returncode != 0:
        source_blockers.append("artistFirstProcessExit")
    gaps = [r["id"] for r in results if r["result"] == "GAP"]
    pending = [r["id"] for r in results if r["result"] == "UNVERIFIED"]
    counts = dict(Counter(r["result"] for r in results))
    report = {"schema": "luhmOs.premonitionTitan500Receipt.v1",
              "identity": "LuHm-OS: Project Premonition", "sourceRef": source,
              "baselineMain": BASE, "sourceOnly": True, "physicalDeviceProven": False,
              "playableGameProven": False, "apkSigningProven": False,
              "crownStatus": "STOP",
              "verdict": "RED_SOURCE" if source_blockers else "AMBER_SOURCE_WITH_GAPS",
              "counts": counts, "criticalSourceBlockers": source_blockers, "knownGaps": gaps, "runtimeUnverified": pending, "checks": results}
    (output / "premonition-titan-500.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# LuHm-OS: Project Premonition | Titan 500 source audit", "",
             f"Source: `{source}`", f"Verdict: **{report['verdict']}** (never device or release GREEN).", "",
             f"Counts: `{counts}`", f"Critical source blockers: `{source_blockers[:25]}`", f"Known feature gaps: `{gaps}`", f"Runtime unverified: `{pending}`", "",
             "200 existing hard-system controls + 120 existing artist-first controls + 180 tracked source/syntax checks.",
             "The final 180 are inventory checks, not functional or runtime validations.",
             "Physical Samsung APK launch, F-Droid signing/update, actual Godot gameplay, Blender exports and funding agreements remain separately unverified.", ""]
    (output / "premonition-titan-500.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"identity": report["identity"], "sourceRef": source, "verdict": report["verdict"],
                      "counts": counts, "criticalSourceBlockers": source_blockers[:30], "knownGaps": gaps, "crownStatus": "STOP"}, indent=2))
    return 2 if source_blockers else 0

if __name__ == "__main__":
    raise SystemExit(main())
