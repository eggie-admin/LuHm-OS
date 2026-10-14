#!/usr/bin/env python3
"""Pick nearest ancestral Belldandy checkpoint, never newest unverified branch."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

PREFIX = "refs/remotes/origin/snapshot/belldandy-"


def git(*args: str, checked: bool = True):
    return subprocess.run(["git", *args], text=True, capture_output=True, check=checked)


def nearest_checkpoint(records: list[tuple[str, int, bool]]) -> tuple[str, int]:
    eligible = [(count, name) for name, count, ancestor in records if ancestor and count >= 0]
    if not eligible:
        return ("NONE_VERIFIED_ANCESTOR", 50)
    count, name = min(eligible)
    return (name, count)


def inspect() -> dict:
    head = git("rev-parse", "HEAD").stdout.strip()
    refs = git("for-each-ref", "--format=%(refname)", PREFIX + "*").stdout.splitlines()
    candidates = []
    for name in refs:
        if not name.startswith(PREFIX):
            continue
        check = git("merge-base", "--is-ancestor", name, "HEAD", checked=False)
        if check.returncode not in (0, 1):
            raise RuntimeError("git ancestry check failed for " + name)
        if check.returncode == 1:
            candidates.append((name, -1, False))
            continue
        count = int(git("rev-list", "--count", name + "..HEAD").stdout.strip())
        candidates.append((name, count, True))
    name, count = nearest_checkpoint(candidates)
    return {"schema": "luhmOs.belldandyCheckpointWindow.v1",
            "sourceRef": head, "checkpoint": name, "commitsSinceCheckpoint": count,
            "status": "STOP_AT_FIFTY" if count >= 50 else "WARN_AT_FORTY" if count >= 40
                      else "CHECKPOINT_DUE" if count >= 25 else "WITHIN_WINDOW",
            "snapshotIsProtectiveOnly": True, "grantsPromotion": False,
            "candidatesChecked": len(candidates)}


def self_test() -> None:
    assert nearest_checkpoint([("recent-nonancestor", 0, False), ("valid-old", 28, True)]) == ("valid-old", 28)
    assert nearest_checkpoint([("old", 45, True), ("nearest", 12, True)]) == ("nearest", 12)
    assert nearest_checkpoint([("future", 0, False)]) == ("NONE_VERIFIED_ANCESTOR", 50)
    assert nearest_checkpoint([]) == ("NONE_VERIFIED_ANCESTOR", 50)
    print("GREEN_BELLDANDY_ANCESTRAL_CHECKPOINT_NEGATIVE_CONTROLS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--github-output", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    result = inspect()
    print(json.dumps(result, sort_keys=True))
    if args.github_output:
        destination = os.environ.get("GITHUB_OUTPUT")
        if not destination:
            raise SystemExit("RED_GITHUB_OUTPUT_MISSING")
        with Path(destination).open("a", encoding="utf-8") as output:
            output.write("latest=" + result["checkpoint"] + "\n")
            output.write("count=" + str(result["commitsSinceCheckpoint"]) + "\n")
            output.write("sourceRef=" + result["sourceRef"] + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
