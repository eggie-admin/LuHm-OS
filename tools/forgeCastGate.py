#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine" / "forgeTwinsV3.json"


def die(message: str, code: int = 2) -> None:
    print(f"FORGE_CAST_GATE=DENIED\nreason={message}")
    raise SystemExit(code)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cast-word", required=True)
    p.add_argument("--milestone-id", required=True)
    p.add_argument("--task-id", required=True)
    p.add_argument("--source-ref", required=True)
    p.add_argument("--actual-source-ref", required=True)
    p.add_argument("--build-scope", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument("--receipt", default=None)
    args = p.parse_args()

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    cast = contract["castEnvelope"]

    if args.cast_word.strip().lower() != cast["castWord"]:
        die("exact Professor CAST word missing")
    if not args.milestone_id.strip():
        die("milestoneId missing")
    if not args.task_id.strip():
        die("taskId missing")
    if args.source_ref != args.actual_source_ref:
        die("requested sourceRef does not equal exact checked-out sourceRef")
    if not args.build_scope.strip():
        die("requestedBuildScope missing")

    allowed_actors = set(cast.get("authorizedGitHubActors", ["eggie-admin"]))
    if args.actor not in allowed_actors:
        die(f"GitHub actor {args.actor!r} is not authorized to represent Professor CAST")

    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=int(cast.get("defaultTtlMinutes", 30)))
    nonce = secrets.token_hex(16)
    nonce_hash = hashlib.sha256(nonce.encode("utf-8")).hexdigest()

    receipt = {
        "schema": "luhm.forge.cast-receipt.v1",
        "castWord": "cast",
        "authorizedBy": "Professor",
        "actor": args.actor,
        "milestoneId": args.milestone_id,
        "taskId": args.task_id,
        "sourceRef": args.source_ref,
        "requestedBuildScope": args.build_scope,
        "issuedAt": now.isoformat(),
        "expiresAt": expires.isoformat(),
        "nonceSha256": nonce_hash,
        "singleUse": True,
        "consumedOnAttempt": True,
        "promotionAuthority": False,
        "releaseAuthority": False,
        "crownAuthority": False,
    }

    if args.receipt:
        out = Path(args.receipt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print("FORGE_CAST_GATE=AUTHORIZED")
    print(f"milestoneId={args.milestone_id}")
    print(f"sourceRef={args.source_ref}")
    print(f"buildScope={args.build_scope}")
    print(f"nonceSha256={nonce_hash}")
    print("NOTE: authorization is one build attempt only and grants no release/deploy/publish/Crown authority")
    return 0


if __name__ == "__main__":
    sys.exit(main())
