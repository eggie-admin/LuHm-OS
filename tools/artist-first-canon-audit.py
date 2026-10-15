#!/usr/bin/env python3
"""Run 120 artist-first source checks; never turn source PASS into runtime GREEN."""
import argparse
from collections import Counter
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def get_path(value, path):
    for part in path.split("."):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value

def evaluate(check):
    if check["kind"] == "runtime":
        return "UNVERIFIED", check["proof"]
    file_path = (root / check["path"]).resolve()
    if not file_path.is_relative_to(root) or not file_path.is_file():
        return "GAP", "Source file unavailable"
    if check["kind"] == "file":
        return "PASS", "Source file present"
    content = file_path.read_text(encoding="utf-8")
    if check["kind"] == "text-includes":
        ok = check["value"] in content
    else:
        try:
            value = get_path(json.loads(content), check["key"])
            if check["kind"] == "json-eq":
                ok = value == check["value"]
            elif check["kind"] == "json-key":
                ok = True
            elif check["kind"] == "json-includes":
                ok = isinstance(value, list) and check["value"] in value
            else:
                raise ValueError("Bad predicate")
        except (KeyError, ValueError, IndexError, TypeError):
            ok = False
    return ("PASS" if ok else "GAP"), ("Matched source" if ok else "Missing or conflicting source")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()
    data = json.loads((root / "doctrine/artist-first-canon-120-checks.json").read_text())
    checks = data["checks"]
    assert data["schema"] == "luhm.artist-first-canon-audit.v1"
    assert data["count"] == len(checks) == 120
    assert len({item["id"] for item in checks}) == 120
    group_counts = Counter(c["domain"] for c in checks)
    assert len(group_counts) == 12
    assert all(n == 10 for n in group_counts.values())
    assert set(group_counts) == set(data["domains"])
    receipts = []
    for item in checks:
        state, evidence = evaluate(item)
        receipts.append({**item, "result": state, "evidence": evidence})
    counts = Counter(x["result"] for x in receipts)
    broken = [x["id"] for x in receipts if x["critical"] and x["result"] != "PASS"]
    report = {"schema": "luhm.artist-first-canon-audit-result.v1",
              "sourceOnly": True, "productReady": False,
              "counts": dict(counts), "criticalFailures": broken, "checks": receipts}
    print(json.dumps({"counts": dict(counts), "criticalFailures": broken}, indent=2))
    if args.output_dir:
        dest = Path(args.output_dir)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "artist-first-120-receipt.json").write_text(json.dumps(report, indent=2) + "\n")
        md = ["# Artist-first canon 120-check audit", "",
              "Source checks only. Runtime work stays unverified until independently tested.", "",
              "| ID | State | Check |", "|---|---|---|"]
        md += ["| " + r["id"] + " | " + r["result"] + " | " + r["label"] + " |" for r in receipts]
        (dest / "artist-first-120-report.md").write_text("\n".join(md) + "\n")
    return 2 if broken else 0

if __name__ == "__main__":
    raise SystemExit(main())
