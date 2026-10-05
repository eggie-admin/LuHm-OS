#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HELP=json.loads((ROOT/"doctrine/commandHelpV1.json").read_text(encoding="utf-8"))
NAMING=json.loads((ROOT/"doctrine/namingNamespaceCanonV1.json").read_text(encoding="utf-8"))
PRECISION=json.loads((ROOT/"doctrine/chatPrecisionCommandV1.json").read_text(encoding="utf-8"))

def vowel_rip(name):
    parts=re.findall(r"[a-z]+|[A-Z][a-z0-9]*|[A-Z]+(?![a-z])|[0-9]+",name)
    out=[]
    for part in parts:
        if not part:
            continue
        first=part[0]
        rest="".join(ch for ch in part[1:] if ch.lower() not in "aeiou")
        out.append(first+rest)
    return "".join(out)

def precision_rows():
    rows=[]
    for item in PRECISION.get("examples",[]):
        canonical=item["camelHump"]
        words=re.findall(r"[a-z]+|[A-Z][a-z0-9]*",canonical)
        shorthand="".join(word[0] for word in words).lower()
        rows.append({
            "canonicalName":canonical,
            "humanMeaning":item.get("humanMeaning","registered LuHm precision command"),
            "purpose":item.get("humanMeaning","registered LuHm precision command"),
            "scope":"command",
            "owner":"lum",
            "aliases":{
                "kebab":item["kebab"],
                "dragonTail":item["debugVerb"],
                "vowelRipped":vowel_rip(canonical),
                "shorthand":shorthand
            },
            "authorityBoundary":"inherits normal LuHm command authority",
            "examples":[f"luhm help {canonical}",f"luhm help {item['kebab']}",f"luhm help {item['debugVerb']}"]
        })
    return rows

def rows():
    return HELP.get("builtins",[])+precision_rows()

def aliases(row):
    values=[row.get("canonicalName","")]
    values.extend(str(v) for v in row.get("aliases",{}).values())
    return [v for v in values if v]

def find(term):
    term=term.strip()
    matches=[row for row in rows() if term in aliases(row)]
    return matches[0] if len(matches)==1 else None

def show_root():
    print("LuHm help")
    print("  luhm -h | --help")
    print("  luhm help <name>")
    print("  luhm <command> -h")
    print("")
    print("Naming")
    print("  camelHump   person-centered canonical identity")
    print("  vowelRipped optional recognizable compression alias")
    print("  shorthand   lowercase registered compact alias")
    print("  kebab-case  lowercase transport/path namespace")
    print("  DRAGONTAIL  uppercase state/sentinel/debug namespace")
    print("")
    print("Commands")
    for row in precision_rows():
        a=row["aliases"]
        print(f"  {a['dragonTail']:<10} {a['kebab']:<22} {row['canonicalName']}")

def show_row(row):
    print(f"{row['canonicalName']}: {row['humanMeaning']}")
    print(f"purpose: {row['purpose']}")
    print(f"scope: {row['scope']}")
    print(f"owner: {row['owner']}")
    print("aliases: "+", ".join(f"{k}={v}" for k,v in row.get("aliases",{}).items()))
    print(f"authority: {row['authorityBoundary']}")
    for ex in row.get("examples",[]):
        print(f"  {ex}")

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if not argv or argv in (["-h"],["--help"]):
        show_root()
        return 0

    if len(argv)>=2 and argv[-1] in ("-h","--help") and argv[0]!="help":
        row=find(argv[0])
        if row is None:
            print(f"VERIFY: unknown or ambiguous help term: {argv[0]}")
            return 2
        show_row(row)
        return 0

    if argv[0]=="help":
        if len(argv)==1:
            show_root()
            return 0
        row=find(argv[1])
        if row is None:
            print(f"VERIFY: unknown or ambiguous help term: {argv[1]}")
            return 2
        show_row(row)
        return 0

    row=find(argv[0])
    if row:
        show_row(row)
        return 0

    print(f"VERIFY: unknown command: {argv[0]}")
    return 2

if __name__=="__main__":
    raise SystemExit(main())
