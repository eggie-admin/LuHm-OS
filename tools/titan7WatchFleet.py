#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "doctrine" / "OPERATION_TITAN7_WATCH_FLEET_V1.json"
SOURCE_TRUTH_PATH = ROOT / "doctrine" / "SOURCE_OF_TRUTH.json"

TEXT_EXTENSIONS = {
    ".cfg", ".conf", ".css", ".example", ".gd", ".godot", ".html", ".ini",
    ".js", ".json", ".md", ".mjs", ".py", ".sh", ".toml", ".tscn", ".txt",
    ".xml", ".yaml", ".yml",
}

SECRET_PATTERNS = {
    "OPENAI_STYLE_KEY": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "GITHUB_PAT": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    "GOOGLE_API_KEY": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}

SELF_EXEMPT = {
    "tools/titan7WatchFleet.py",
}

BUILD_PRIMITIVES = (
    "--export-debug",
    "--export-release",
    "gradlew assemble",
    "gradlew bundle",
    "npm run build",
    "pnpm build",
    "yarn build",
    "cargo build",
    "cmake --build",
    "docker build",
)

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def tracked_paths() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / item.decode("utf-8") for item in raw.split(b"\0") if item]

def read_texts(paths: list[Path]) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in paths:
        rel = str(path.relative_to(ROOT))
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {".gitignore", "LICENSE"}:
            continue
        try:
            out[rel] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return out

def result(watch_id: str, state: str, detail: str, evidence=None) -> dict:
    item = {"id": watch_id, "state": state, "detail": detail}
    if evidence:
        item["evidence"] = evidence
    return item

def evaluate(manifest: dict, texts: dict[str, str]) -> list[dict]:
    source = json.loads(SOURCE_TRUTH_PATH.read_text(encoding="utf-8"))
    results: list[dict] = []

    for watch in manifest["watches"]:
        wid = watch["id"]
        mode = watch["mode"]

        if mode == "manualDevice":
            results.append(result(wid, "WAIT_HUMAN", "Physical-device receipt required; repo state alone cannot satisfy this watch."))
            continue
        if mode in {"externalGitHub", "externalWeb", "externalRuntime", "externalDrive"}:
            results.append(result(wid, "UNKNOWN_EXTERNAL", f"{mode} evidence must be supplied by its connector/watch lane."))
            continue
        if mode == "aggregate":
            continue

        if wid == "canonicalMainIdentity":
            errors = []
            if source.get("canonical_repository") != "eggie-admin/LuHm-OS":
                errors.append("canonical_repository drift")
            if source.get("authority") != "Professor":
                errors.append("authority drift")
            if source.get("promotion") is not False:
                errors.append("unexpected promotion=true")
            state = "RED" if errors else "GREEN"
            results.append(result(wid, state, "; ".join(errors) if errors else "Canonical repository/authority/promotion boundary is coherent."))
            continue

        if wid == "sourceTruthDrift":
            live = source.get("liveReconciliation")
            historical = source.get("reconciliation")
            if live and live.get("crownStatus") == "STOP":
                results.append(result(wid, "GREEN", "Live reconciliation metadata exists and historical reconciliation remains separable."))
            elif historical:
                results.append(result(wid, "AMBER", "Historical reconciliation exists but no live reconciliation block is present on this source."))
            else:
                results.append(result(wid, "RED", "No reconciliation metadata found."))
            continue

        if wid == "workflowPermissions":
            reds, ambers = [], []
            for rel, text in texts.items():
                if not rel.startswith(".github/workflows/"):
                    continue
                if re.search(r"(?m)^\s*permissions:\s*write-all\s*$", text):
                    reds.append(rel)
                if "pull_request_target:" in text:
                    ambers.append(rel)
            if reds:
                results.append(result(wid, "RED", "write-all workflow permission found.", reds))
            elif ambers:
                results.append(result(wid, "AMBER", "pull_request_target trust boundary requires review.", ambers))
            else:
                results.append(result(wid, "GREEN", "No write-all or pull_request_target workflow found."))
            continue

        if wid == "actionPinning":
            mutable = []
            for rel, text in texts.items():
                if not rel.startswith(".github/workflows/"):
                    continue
                for m in re.finditer(r"uses:\s*(actions/[^\s#]+@v\d+)\b", text):
                    mutable.append({"path": rel, "ref": m.group(1)})
            results.append(result(
                wid,
                "AMBER" if mutable else "GREEN",
                "Mutable major action tags remain." if mutable else "All detected actions/* references are immutable or non-major refs.",
                mutable or None,
            ))
            continue

        if wid == "secretLeakage":
            hits = []
            for rel, text in texts.items():
                if rel in SELF_EXEMPT:
                    continue
                for name, pattern in SECRET_PATTERNS.items():
                    if pattern.search(text):
                        hits.append({"path": rel, "kind": name})
            results.append(result(
                wid,
                "RED" if hits else "GREEN",
                "Secret-like material detected." if hits else "No tracked secret-like literals detected by Titan7 heuristics.",
                hits or None,
            ))
            continue

        if wid == "legacyLanLane":
            hits = [rel for rel, text in texts.items() if ".lan" in text]
            results.append(result(
                wid,
                "AMBER" if hits else "GREEN",
                f"{len(hits)} tracked files still reference .lan." if hits else "No tracked .lan reference remains.",
                hits or None,
            ))
            continue

        if wid == "forgeIdentity":
            legacy = (ROOT / "agents" / "buildOnis").exists()
            canonical = (ROOT / "agents" / "forgeOniTwins").exists()
            if canonical and not legacy:
                state, detail = "GREEN", "forgeOniTwins is canonical and legacy buildOnis path is absent."
            elif canonical and legacy:
                state, detail = "AMBER", "forgeOniTwins exists but buildOnis legacy path remains."
            elif legacy:
                state, detail = "AMBER", "buildOnis remains present and forgeOniTwins has not landed on this source."
            else:
                state, detail = "RED", "Neither forgeOniTwins nor legacy buildOnis path exists."
            results.append(result(wid, state, detail))
            continue

        if wid == "forgeCastBoundary":
            contract = ROOT / "doctrine" / "FORGE_TWINS_V3.json"
            gate = ROOT / "tools" / "forgeCastGate.py"
            if contract.is_file() and gate.is_file():
                c = json.loads(contract.read_text(encoding="utf-8"))
                ok = (
                    c.get("crownStatus") == "STOP"
                    and c.get("authority") == "Professor"
                    and c.get("castEnvelope", {}).get("castWord") == "cast"
                    and c.get("castEnvelope", {}).get("persistentAuthorizationAllowed") is False
                )
                results.append(result(wid, "GREEN" if ok else "RED", "CAST contract present and bounded." if ok else "CAST contract present but authority/boundary drift detected."))
            else:
                build_auto = []
                for rel, text in texts.items():
                    if not rel.startswith(".github/workflows/"):
                        continue
                    if any(p.lower() in text.lower() for p in BUILD_PRIMITIVES) and (
                        "pull_request:" in text or re.search(r"(?m)^\s*push:\s*$", text)
                    ):
                        build_auto.append(rel)
                results.append(result(
                    wid,
                    "AMBER",
                    "Forge CAST contract has not landed on this source; build-producing workflow review remains separate.",
                    build_auto or None,
                ))
            continue

        if wid == "assetProvenance":
            owned = any("rights" in rel.lower() or "license" in rel.lower() for rel in texts)
            results.append(result(
                wid,
                "GREEN" if owned else "AMBER",
                "Tracked rights/license material exists for provenance review." if owned else "No obvious tracked rights/license registry detected.",
            ))
            continue

        if wid == "dependencyDrift":
            broad = []
            for rel, text in texts.items():
                low = rel.lower()
                if not any(token in low for token in ("requirements", "package.json", "pyproject", "dependencies")):
                    continue
                if re.search(r'["\']\^\d|["\']~\d|>=\s*\d', text):
                    broad.append(rel)
            results.append(result(
                wid,
                "AMBER" if broad else "GREEN",
                "Broad dependency ranges detected for review." if broad else "No obvious broad ranges detected by the local heuristic.",
                sorted(set(broad)) or None,
            ))
            continue

        results.append(result(wid, "AMBER", "Watch is defined but has no repo-local evaluator yet."))

    red = [r for r in results if r["state"] == "RED"]
    amber = [r for r in results if r["state"] == "AMBER"]
    wait = [r for r in results if r["state"] in {"WAIT_HUMAN", "UNKNOWN_EXTERNAL"}]
    if red:
        agg_state = "RED"
    elif amber or wait:
        agg_state = "AMBER"
    else:
        agg_state = "GREEN"

    results.append(result(
        "currentMilestone",
        agg_state,
        f"RED={len(red)} AMBER={len(amber)} EXTERNAL_OR_HUMAN={len(wait)}",
    ))
    return results

def markdown(report: dict) -> str:
    lines = [
        "# OperationTitan7 Watch Fleet v1",
        "",
        f"- Status: **{report['status']}**",
        f"- Exact source: `{report['sourceCommit']}`",
        f"- Watches: **{report['watchCount']}**",
        f"- RED: **{report['counts'].get('RED', 0)}**",
        f"- AMBER: **{report['counts'].get('AMBER', 0)}**",
        f"- UNKNOWN_EXTERNAL: **{report['counts'].get('UNKNOWN_EXTERNAL', 0)}**",
        f"- WAIT_HUMAN: **{report['counts'].get('WAIT_HUMAN', 0)}**",
        "",
    ]
    for item in report["results"]:
        lines.append(f"- **{item['state']}** `{item['id']}`: {item['detail']}")
    lines += [
        "",
        "This fleet is read-only evidence collection. It grants no build, merge, deploy, signing, publication, Shizuku, or Crown authority.",
        "",
    ]
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=ROOT / "build/titan7-watch-fleet/report.json")
    parser.add_argument("--markdown", type=Path, default=ROOT / "build/titan7-watch-fleet/report.md")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    paths = tracked_paths()
    texts = read_texts(paths)
    results = evaluate(manifest, texts)

    counts = {}
    for item in results:
        counts[item["state"]] = counts.get(item["state"], 0) + 1

    status = "RED_TITAN7_WATCH_FLEET" if counts.get("RED", 0) else (
        "AMBER_TITAN7_WATCH_FLEET" if any(counts.get(k, 0) for k in ("AMBER", "UNKNOWN_EXTERNAL", "WAIT_HUMAN"))
        else "GREEN_TITAN7_WATCH_FLEET"
    )

    report = {
        "schema": "luhm-os.operation-titan7-watch-fleet-report.v1",
        "status": status,
        "sourceCommit": git("rev-parse", "HEAD"),
        "authority": "Professor",
        "sourceLaw": manifest["sourceLaw"],
        "watchCount": len(manifest["watches"]),
        "counts": counts,
        "results": results,
        "mutationAuthority": False,
        "buildAuthority": False,
        "publicationAuthority": False,
        "productionSigningAuthority": False,
        "crownStatus": "STOP",
    }

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(report) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": status,
        "sourceCommit": report["sourceCommit"],
        "watchCount": report["watchCount"],
        "counts": counts,
    }, indent=2))

    return 2 if counts.get("RED", 0) else 0

if __name__ == "__main__":
    raise SystemExit(main())
