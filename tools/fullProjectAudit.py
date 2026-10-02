#!/usr/bin/env python3
"""LuHm OS whole-repository fail-closed static audit.

This tool is intentionally read-only. It inventories every tracked file, runs
available syntax checks, scans for security/authority drift, and emits evidence.
It does not merge, publish, sign, deploy, or change repository state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTENSIONS = {
    ".cfg", ".conf", ".css", ".example", ".gd", ".gitignore", ".godot", ".html",
    ".ini", ".js", ".json", ".md", ".mjs", ".py", ".sh", ".svg", ".toml",
    ".tscn", ".txt", ".xml", ".yaml", ".yml",
}

SECRET_PATTERNS = {
    "OPENAI_STYLE_KEY": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "GITHUB_PAT": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    "GOOGLE_API_KEY": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}

ALLOWED_WILDCARD_BIND_PATHS = {
    "host/mcp/luhmHarnessServer.py",
    "host/mcp/luhmMcpServer.py",
    "tools/pluginPublicationAudit.py",
    "tools/renderHarnessLiveAudit.py",
    "doctrine/openAiLumOniDeployment-20260927.json",
    "plugins/luhm-os/README.md",
}

HISTORICAL_LAN_PREFIXES = (
    "installPortal/",
    "doctrine/fqdnInstallPortal",
    "doctrine/fullSourceTruthAudit-20260926.json",
)

HEURISTIC_SELF_EXEMPT = {
    "tools/fullProjectAudit.py",
}

JSON_TEMPLATE_EXCEPTIONS = {
    "installPortal/manifest.template.json",
}

class StrictHTMLParser(HTMLParser):
    pass

@dataclass
class Finding:
    severity: str
    code: str
    path: str
    detail: str

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def tracked_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / p.decode("utf-8") for p in raw.split(b"\0") if p]

def add(findings: list[Finding], severity: str, code: str, path: str, detail: str) -> None:
    findings.append(Finding(severity, code, path, detail))

def check_json(rel: str, text: str, findings: list[Finding]) -> None:
    try:
        json.loads(text)
    except Exception as exc:
        add(findings, "RED", "INVALID_JSON", rel, str(exc))

def check_python(rel: str, text: str, findings: list[Finding]) -> None:
    try:
        compile(text, rel, "exec")
    except SyntaxError as exc:
        add(findings, "RED", "PYTHON_SYNTAX", rel, f"{exc.msg} line={exc.lineno}")

def run_syntax(command: list[str], rel: str, code: str, findings: list[Finding]) -> None:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode:
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        add(findings, "RED", code, rel, (detail[-1] if detail else f"exit={proc.returncode}")[:500])

def check_html(rel: str, text: str, findings: list[Finding]) -> None:
    try:
        parser = StrictHTMLParser(convert_charrefs=True)
        parser.feed(text)
        parser.close()
    except Exception as exc:
        add(findings, "RED", "HTML_PARSE", rel, str(exc))

def check_xml(rel: str, text: str, findings: list[Finding]) -> None:
    try:
        ElementTree.fromstring(text)
    except Exception as exc:
        add(findings, "RED", "XML_PARSE", rel, str(exc))

def scan_content(rel: str, text: str, findings: list[Finding]) -> None:
    for code, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            add(findings, "RED", code, rel, "Secret-like literal appears in tracked text.")

    if re.search(r"\bchmod\s+777\b", text):
        add(findings, "RED", "CHMOD_777", rel, "World-writable chmod detected.")
    if re.search(r"curl[^\n|]*\|\s*(?:bash|sh)\b", text, re.I):
        add(findings, "RED", "PIPE_TO_SHELL", rel, "Network download piped directly to a shell.")
    if re.search(r"\bpermissions:\s*write-all\b", text):
        add(findings, "RED", "ACTIONS_WRITE_ALL", rel, "GitHub workflow grants write-all.")
    if "pull_request_target" in text:
        add(findings, "AMBER", "PULL_REQUEST_TARGET", rel, "Review pull_request_target trust boundary.")

    if ".lan" in text:
        if rel.startswith(HISTORICAL_LAN_PREFIXES):
            add(findings, "AMBER", "LEGACY_LAN_HISTORICAL", rel, "Historical/private-LAN lane still uses .lan; do not treat it as current host doctrine.")
        else:
            add(findings, "AMBER", "LEGACY_LAN", rel, "Contains .lan naming outside the historical install-portal lane.")

    if re.search(r"\bluhmos-main\b", text, re.I):
        add(findings, "AMBER", "LEGACY_BRANCH_NAME", rel, "Contains luhmos-main; current canonical repository branch is main.")
    if re.search(r"\bvercel\b", text, re.I):
        add(findings, "AMBER", "RETIRED_VENDOR_REFERENCE", rel, "Contains Vercel reference; verify historical/retired context.")
    if re.search(r"\bbuildOnis\b", text):
        add(findings, "AMBER", "LEGACY_BUILD_ONIS", rel, "Legacy buildOnis name remains; current naming doctrine prefers forgeOniTwins.")

    if "0.0.0.0" in text and rel not in ALLOWED_WILDCARD_BIND_PATHS:
        add(findings, "AMBER", "WILDCARD_BIND_REVIEW", rel, "Contains 0.0.0.0 outside the explicit Render/MCP allowlist.")

    if rel.startswith(".github/workflows/"):
        for match in re.finditer(r"uses:\s*([^\s#]+)", text):
            ref = match.group(1)
            if re.match(r"actions/[^@]+@v\d+$", ref, re.I):
                add(findings, "AMBER", "MUTABLE_ACTION_TAG", rel, f"Workflow uses mutable major tag: {ref}")

    if re.search(r"\b(?:TODO|FIXME|HACK|XXX)\b", text):
        add(findings, "INFO", "WORK_MARKER", rel, "Contains TODO/FIXME/HACK/XXX.")

def doctrine_checks(files: dict[str, str], head: str, findings: list[Finding]) -> None:
    source_text = files.get("doctrine/SOURCE_OF_TRUTH.json")
    if not source_text:
        add(findings, "RED", "MISSING_SOURCE_OF_TRUTH", "doctrine/SOURCE_OF_TRUTH.json", "Canonical doctrine file missing.")
        return
    source = json.loads(source_text)

    if source.get("canonical_repository") != "eggie-admin/LuHm-OS":
        add(findings, "RED", "CANONICAL_REPOSITORY_DRIFT", "doctrine/SOURCE_OF_TRUTH.json", str(source.get("canonical_repository")))
    if source.get("authority") != "Professor":
        add(findings, "RED", "AUTHORITY_DRIFT", "doctrine/SOURCE_OF_TRUTH.json", str(source.get("authority")))
    if source.get("promotion") is not False:
        add(findings, "RED", "UNEXPECTED_PROMOTION", "doctrine/SOURCE_OF_TRUTH.json", "promotion must remain false absent explicit promoted release evidence.")

    reconciliation = source.get("reconciliation", {})
    observed = reconciliation.get("observedMain")
    if observed and observed != head:
        add(findings, "AMBER", "RECONCILIATION_BASELINE_OLD", "doctrine/SOURCE_OF_TRUTH.json",
            f"reconciliation.observedMain={observed} while audited HEAD={head}; preserve as historical proof, not current live identity.")

    milestone = source.get("currentMainSourceTruthMilestone", {})
    baseline = milestone.get("baseCanonicalMain")
    if baseline and baseline != head:
        add(findings, "AMBER", "CURRENT_MAIN_MILESTONE_BASELINE_OLD", "doctrine/SOURCE_OF_TRUTH.json",
            f"currentMainSourceTruthMilestone.baseCanonicalMain={baseline} while audited HEAD={head}.")

    if (ROOT / "agents/buildOnis").exists():
        add(findings, "AMBER", "LEGACY_AGENT_PATH", "agents/buildOnis",
            "Legacy path still canonical on main; migrate or explicitly document alias to forgeOniTwins.")

    frontend_workflow = files.get(".github/workflows/frontend-jquery-dryrun.yml", "")
    if "actions/checkout@v4" in frontend_workflow or "actions/setup-node@v4" in frontend_workflow:
        add(findings, "AMBER", "FRONTEND_WORKFLOW_ACTION_PINNING", ".github/workflows/frontend-jquery-dryrun.yml",
            "Frontend workflow still uses mutable major action tags while most LuHm workflows are SHA-pinned.")

def self_test() -> None:
    findings: list[Finding] = []
    secret = "sk-" + "A" * 28
    scan_content("synthetic.txt", secret, findings)
    assert any(f.code == "OPENAI_STYLE_KEY" and f.severity == "RED" for f in findings)
    findings.clear()
    scan_content(".github/workflows/x.yml", "steps:\n - uses: actions/checkout@v4\n", findings)
    assert any(f.code == "MUTABLE_ACTION_TAG" for f in findings)
    findings.clear()
    scan_content("x.sh", "curl https://example.invalid/x | bash\n", findings)
    assert any(f.code == "PIPE_TO_SHELL" and f.severity == "RED" for f in findings)
    print("FULL_PROJECT_AUDIT_NEGATIVE_CONTROLS=PASS")

def audit() -> dict:
    head = git("rev-parse", "HEAD")
    paths = tracked_files()
    findings: list[Finding] = []
    inventory: list[dict] = []
    text_cache: dict[str, str] = {}

    node = shutil.which("node")
    ruby = shutil.which("ruby")
    bash = shutil.which("bash")

    for path in paths:
        rel = str(path.relative_to(ROOT))
        suffix = path.suffix.lower()
        raw = path.read_bytes()
        item = {
            "path": rel,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "kind": "binary",
            "checks": [],
        }

        is_text = suffix in TEXT_EXTENSIONS or path.name in {".gitignore", "LICENSE"}
        if not is_text:
            inventory.append(item)
            continue

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            add(findings, "RED", "UTF8_DECODE", rel, str(exc))
            inventory.append(item)
            continue

        item["kind"] = "text"
        text_cache[rel] = text
        if rel not in HEURISTIC_SELF_EXEMPT:
            scan_content(rel, text, findings)
        else:
            item["checks"].append("heuristic-self-exempt")

        if suffix == ".json":
            if rel in JSON_TEMPLATE_EXCEPTIONS:
                item["checks"].append("json-template")
            else:
                check_json(rel, text, findings)
                item["checks"].append("json")
        elif suffix == ".py":
            check_python(rel, text, findings)
            item["checks"].append("python-compile")
        elif suffix == ".sh" and bash:
            run_syntax([bash, "-n", str(path)], rel, "BASH_SYNTAX", findings)
            item["checks"].append("bash-n")
        elif suffix in {".js", ".mjs"} and node:
            run_syntax([node, "--check", str(path)], rel, "NODE_SYNTAX", findings)
            item["checks"].append("node-check")
        elif suffix == ".html":
            check_html(rel, text, findings)
            item["checks"].append("html-parser")
        elif suffix in {".svg", ".xml"}:
            check_xml(rel, text, findings)
            item["checks"].append("xml-parser")
        elif suffix in {".yml", ".yaml"} and ruby:
            command = [ruby, "-e", "require 'yaml'; YAML.load_file(ARGV[0], aliases: true)", str(path)]
            run_syntax(command, rel, "YAML_PARSE", findings)
            item["checks"].append("ruby-yaml")

        inventory.append(item)

    doctrine_checks(text_cache, head, findings)

    counts = {"RED": 0, "AMBER": 0, "INFO": 0}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1

    status = "RED_FULL_PROJECT_AUDIT" if counts["RED"] else (
        "AMBER_FULL_PROJECT_AUDIT_ACTIONS_PENDING" if counts["AMBER"] else "GREEN_FULL_PROJECT_AUDIT"
    )

    return {
        "schema": "luhm-os.full-project-audit.v1",
        "status": status,
        "sourceCommit": head,
        "authority": "Professor",
        "sourceLaw": "AI proposes. Policy authorizes. CI proves. Human promotes.",
        "trackedFileCount": len(paths),
        "trackedBytes": sum(item["bytes"] for item in inventory),
        "textFileCount": sum(item["kind"] == "text" for item in inventory),
        "binaryFileCount": sum(item["kind"] == "binary" for item in inventory),
        "findingCounts": counts,
        "findings": [asdict(f) for f in findings],
        "inventory": inventory,
        "mutationAuthority": False,
        "releaseAuthority": False,
        "publicationAuthority": False,
        "productionSigningAuthority": False,
        "crownStatus": "STOP",
    }

def markdown(report: dict) -> str:
    lines = [
        "# LuHm OS Full Project Audit",
        "",
        f"- Status: **{report['status']}**",
        f"- Exact source: `{report['sourceCommit']}`",
        f"- Tracked files audited: **{report['trackedFileCount']}**",
        f"- RED: **{report['findingCounts']['RED']}**",
        f"- AMBER: **{report['findingCounts']['AMBER']}**",
        f"- INFO: **{report['findingCounts']['INFO']}**",
        "",
        "## Findings",
        "",
    ]
    for f in report["findings"]:
        lines.append(f"- **{f['severity']} {f['code']}** `{f['path']}` — {f['detail']}")
    lines += [
        "",
        "## Authority",
        "",
        "This audit is evidence only. It grants no merge, release, signing, publication, deployment, runtime, or Crown authority.",
        "",
    ]
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", type=Path, default=ROOT / "build/full-project-audit/report.json")
    parser.add_argument("--markdown", type=Path, default=ROOT / "build/full-project-audit/report.md")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    report = audit()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(report) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "sourceCommit", "trackedFileCount", "findingCounts")}, indent=2))

    if report["findingCounts"]["RED"]:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
