#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

PROFILE_PATHS={
    "default":"doctrine/founderEscalationLadderV1.json",
    "corporate":"doctrine/corporateEscalationProfileV1.json",
    "magic":"doctrine/magicEscalationProfileV1.json",
    "art":"doctrine/yumeCreativeEscalationV1.json",
    "technology":"doctrine/operationTitan7ChatTriggerV2.json",
}

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def _check_profile_authority(domain, data):
    """Source profiles select routing, never Crown authority."""
    if (data.get("authority")!="Professor" or
            data.get("kernel")!="doctrine/escalationKernelV1.json" or
            data.get("crownStatus")!="STOP"):
        raise RuntimeError(f"RED_{domain.upper()}_AUTHORITY")
    if domain=="technology":
        if (data.get("promotion") is not False or
                data.get("escalationTierMap")!={"technologyFastPath":0,
                  "forFuckSake":1,"scorchedEarth":2,"finalForm":3}):
            raise RuntimeError("RED_TECHNOLOGY_PROMOTION_OR_TIERS")


def _check_kernel_contract(kernel):
    matrix=kernel.get("fourByFourModel",{})
    if (kernel.get("schema")!="luhmOs.escalationKernel.v1" or
            kernel.get("authority")!="Professor" or kernel.get("crownStatus")!="STOP" or
            matrix.get("horizontalBeats")!=["hear","resolve","act","verify"] or
            matrix.get("verticalTiers")!=[0,1,2,3] or
            kernel.get("fastPathLaw",{}).get("automaticMachineContinuation") is not True):
        raise RuntimeError("RED_ESCALATION_KERNEL_CONTRACT")


def normalize_profile(domain):
    if domain not in PROFILE_PATHS:
        raise ValueError(f"unsupported domain: {domain}")
    data=load(PROFILE_PATHS[domain])
    _check_profile_authority(domain,data)

    if domain!="technology":
        tiers=data.get("tiers",[])
        if [x.get("tier") for x in tiers] != [0,1,2,3]:
            raise RuntimeError(f"RED_{domain.upper()}_TIER_SHAPE")
        return tiers

    rooms=load("doctrine/escalationWorkflowRoomsV1.json")
    fast=rooms.get("defaultFastPathRoom",{})
    if (rooms.get("crownStatus")!="STOP" or
            fast.get("tier")!=0 or fast.get("id")!="technologyFastPath"):
        raise RuntimeError("RED_TECHNOLOGY_ROOM_CONTRACT")
    esc=data.get("escalations",{})
    return [
        {
            "tier":0,
            "id":"technologyFastPath",
            "title":"Technology FAST_PATH",
            "lead":"lum",
            "purpose":data.get("tierZero",{}).get("meaning","UNKNOWN"),
            "room":rooms.get("defaultFastPathRoom",{}),
        },
        {
            "tier":1,
            "id":"forFuckSake",
            "title":"FFS 25-pass",
            "lead":"lum",
            "purpose":esc.get("forFuckSake",{}).get("meaning","UNKNOWN"),
            "room":rooms.get("rooms",{}).get("forFuckSake",{}),
        },
        {
            "tier":2,
            "id":"scorchedEarth",
            "title":"Scorched Earth 50-pass",
            "lead":"lum",
            "purpose":esc.get("scorchedEarth",{}).get("meaning","UNKNOWN"),
            "room":rooms.get("rooms",{}).get("scorchedEarth",{}),
        },
        {
            "tier":3,
            "id":"finalForm",
            "title":"Final Form",
            "lead":"lum",
            "purpose":esc.get("finalForm",{}).get("meaning","UNKNOWN"),
            "room":rooms.get("rooms",{}).get("finalForm",{}),
        },
    ]

def plan(domain,tier,outcome):
    kernel=load("doctrine/escalationKernelV1.json")
    _check_kernel_contract(kernel)
    if type(tier) is not int or tier not in range(4):
        raise ValueError("tier must be 0..3")
    if outcome not in ("working","green","blocked","unknown","conflict"):
        raise ValueError("INVALID_OUTCOME")
    tiers=normalize_profile(domain)
    current=tiers[tier]

    if outcome=="green":
        decision="CLOSE_OR_DEESCALATE"
        next_tier=max(0,tier-1) if tier>0 else 0
    elif outcome=="blocked":
        if tier<3:
            decision="ESCALATE"
            next_tier=tier+1
        else:
            decision="HOLD_TIER_3_BLOCKER"
            next_tier=3
    elif outcome in ("unknown","conflict"):
        decision="HOLD_AND_DIAGNOSE"
        next_tier=tier
    else:
        decision="CONTINUE_CURRENT_TIER"
        next_tier=tier

    return {
        "schema":"luhmOs.escalationPlan.v1",
        "domain":domain,
        "currentTier":tier,
        "current":current,
        "outcome":outcome.upper(),
        "decision":decision,
        "nextTier":next_tier,
        "next":tiers[next_tier],
        "commonState":kernel.get("commonState",[]),
        "fastPathLaw":kernel.get("fastPathLaw",{}),
        "authorityBoundary":{
            "tierChangesAuthority":False,
            "providerMayGrantGreen":False,
            "professorRetainsCrown":True,
            "mutationAuthority":False,
        },
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--domain",required=True,choices=tuple(PROFILE_PATHS))
    parser.add_argument("--tier",required=True,type=int)
    parser.add_argument("--outcome",default="working",choices=("working","green","blocked","unknown","conflict"))
    args=parser.parse_args()
    print(json.dumps(plan(args.domain,args.tier,args.outcome),indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
