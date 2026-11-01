#!/usr/bin/env python3
"""LuHm offline creative CLI. Reads only bounded explicitly provided standard input."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import creativeCommunityAudit as forge


def main()->int:
    parser=argparse.ArgumentParser(description="LuHm local creative source inspector")
    subs=parser.add_subparsers(dest="command",required=True)
    subs.add_parser("audit",help="check four-by-four source registry")
    subs.add_parser("feed-stdin",help="parse at most 64 KiB of provided RSS/Atom bytes, no network")
    c=subs.add_parser("reference",help="plan rights review for a registered source")
    c.add_argument("--task-id",required=True)
    c.add_argument("--source-ref",required=True)
    c.add_argument("--scope-id",required=True)
    c.add_argument("--id",required=True)
    c.add_argument("--license",required=True)
    a=subs.add_parser("avatar",help="inspect a proposed avatar retargeting plan")
    a.add_argument("--source",required=True)
    a.add_argument("--target",required=True)
    a.add_argument("--rights",required=True)
    args=parser.parse_args()
    try:
        if args.command=="audit":
            result=forge.audit()
        elif args.command=="feed-stdin":
            payload=sys.stdin.buffer.read(forge.MAX_FEED+1)
            result=forge.parse_feed(payload)
        elif args.command=="reference":
            result=forge.candidate(
                task_id=args.task_id,source_ref=args.source_ref,
                scope_id=args.scope_id,reference_id=args.id,
                asset_license=args.license)
        elif args.command=="avatar":
            result=forge.avatar_retarget_plan(
                source_format=args.source,target_format=args.target,rights=args.rights)
        else:
            raise ValueError("RED_CREATIVE_COMMAND")
    except ValueError as exc:
        print(json.dumps({"state":"STOP_INVALID_INPUT","reason":str(exc)}))
        return 2
    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
