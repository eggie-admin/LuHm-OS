#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HELP=json.loads((ROOT/"doctrine/commandHelpV1.json").read_text(encoding="utf-8"))
NAMING=json.loads((ROOT/"doctrine/namingNamespaceCanonV1.json").read_text(encoding="utf-8"))

def rows():
    return HELP.get("builtins",[])

def aliases(row):
    values=[row.get("canonicalName","")]
    values.extend(str(v) for v in row.get("aliases",{}).values())
    return [v for v in values if v]

def find(term):
    t=term.strip()
    for row in rows():
        if t in aliases(row):
            return row
    return None

def show_root():
    print("LuHm help")
    print("  luhm -h | --help")
    print("  luhm help <name>")
    print("Naming:")
    print("  camelHump  person-centered canonical name")
    print("  vowelRipped optional compression alias")
    print("  shorthand   lowercase registered alias")
    print("  kebab-case  lowercase transport/path namespace")
    print("  DRAGONTAIL  uppercase state/sentinel namespace")

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
    args=parser.parse_args()
    if args.help or not args.verb:
        show_root(); return 0
    if args.verb=="help":
        if not args.term:
            show_root(); return 0
        row=find(args.term)
        if row is None:
            print(f"VERIFY: unknown help term: {args.term}")
            return 2
        show_row(row); return 0
    row=find(args.verb)
    if row:
        show_row(row); return 0
    print(f"VERIFY: unknown command: {args.verb}")
    return 2

if __name__=="__main__":
    raise SystemExit(main())
