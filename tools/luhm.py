#!/usr/bin/env python3
import argparse
import json
import re
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
        shorthand="".join(word[0] for word in re.findall(r"[a-z]+|[A-Z][a-z0-9]*",canonical)).lower()
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
    if len(matches)==1:
        return matches[0]
    return None

def show_root():
    print("LuHm help")
    print("  luhm -h | --help")
    print("  luhm help <name>")
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

def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h","--help",action="store_true")
    parser.add_argument("verb",nargs="?")
    parser.add_argument("term",nargs="?")
    parser.add_argument("tail",nargs="?")
    args=parser.parse_args()
    if args.help or not args.verb:
        show_root()
        return 0
    if args.tail in ("-h","--help"):
        row=find(args.verb)
        if row:
            show_row(row)
            return 0
    if args.verb=="help":
        if not args.term:
            show_root()
            return 0
        row=find(args.term)
        if row is None:
            print(f"VERIFY: unknown or ambiguous help term: {args.term}")
            return 2
        show_row(row)
        return 0
    row=find(args.verb)
    if row:
        show_row(row)
        return 0
    print(f"VERIFY: unknown command: {args.verb}")
    return 2

if __name__=="__main__":
    raise SystemExit(main())
