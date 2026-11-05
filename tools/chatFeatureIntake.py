#!/usr/bin/env python3
"""Validate a scoped in-chat studio feature request; never execute or promote it."""
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
KINDS = {"htmlUi", "gameplay", "artPipeline", "backend"}
def validate(request):
    if not isinstance(request, dict):
        raise ValueError("object required")
    if set(request) != {"taskId", "sourceRef", "kind", "request"}:
        raise ValueError("exact taskId/sourceRef/kind/request fields required")
    if not re.fullmatch(r"[a-z][A-Za-z0-9]{2,63}", request["taskId"]):
        raise ValueError("invalid taskId")
    if not SHA.fullmatch(request["sourceRef"]):
        raise ValueError("invalid exact sourceRef")
    if request["kind"] not in KINDS:
        raise ValueError("unsupported kind")
    description = request["request"]
    if not isinstance(description, str) or not 3 <= len(description.strip()) <= 1000:
        raise ValueError("request must be 3..1000 characters")
    return {"schema": "luhm.studioFeatureIntake.v1", **request,
            "lane": "proposed", "status": "AMBER_UNEXECUTED",
            "mutationAuthorized": False, "deploymentAuthorized": False,
            "nextAction": "create supervised scoped draft and run exact-source CI"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--output", default="build/feature-intake/receipt.json")
    a = p.parse_args()
    result = validate(json.loads(Path(a.input).read_text(encoding="utf-8")))
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
if __name__ == "__main__":
    main()
