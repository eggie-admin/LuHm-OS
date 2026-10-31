#!/usr/bin/env python3
"""Local/offline first-encounter dating-sim runner. No AI, eval, disk writes or network."""
import argparse
import json
from pathlib import Path
from tools.hydraCastMediaBridge import STORY,verify_story

def new_game(story):
    if verify_story(story):raise ValueError("INVALID_STORY")
    return {"nodeId":story["entry"],"affinity":story["state"]["defaultAffinity"],"history":[]}

def current(story,state):
    return next(n for n in story["nodes"] if n["id"]==state["nodeId"])

def select(story,state,choice_index):
    if verify_story(story):raise ValueError("INVALID_STORY")
    if type(choice_index) is not int:raise ValueError("CHOICE_TYPE")
    node=current(story,state)
    if node["kind"]=="ending":raise ValueError("ALREADY_ENDING")
    choices=node["choices"]
    if not 0<=choice_index<len(choices):raise ValueError("CHOICE_RANGE")
    if len(state["history"])>=16:raise ValueError("STEP_LIMIT")
    choice=choices[choice_index]
    lo,hi=story["state"]["minAffinity"],story["state"]["maxAffinity"]
    affection=max(lo,min(hi,state["affinity"]+choice["affinityDelta"]))
    return {"nodeId":choice["next"],"affinity":affection,
            "history":[*state["history"],{"from":node["id"],"choiceIndex":choice_index}]}
def demo(story):
    state=new_game(story)
    while current(story,state)["kind"]!="ending":
        state=select(story,state,0)
    return {"status":"LOCAL_TEXT_PILOT_COMPLETED","ending":state["nodeId"],"affinity":state["affinity"],
            "steps":len(state["history"]),"unrealBuilt":False,"providerCalled":False,"crown":"STOP"}
def play(story):
    state=new_game(story)
    print("Crown Cathedral | First Encounter (private offline pilot)")
    while True:
        node=current(story,state)
        print(f"\n{node['speaker']}: {node['line']}")
        if node["kind"]=="ending":
            print(f"End of rehearsal | affinity={state['affinity']}/10")
            return
        for i,c in enumerate(node["choices"],1):print(f" {i}. {c['label']}")
        try:
            choice=input("Choose number (q to quit): ").strip()
        except (EOFError,KeyboardInterrupt):
            print("\nRehearsal closed.")
            return
        if choice.lower()=="q":return
        if not choice.isdecimal():print("Select a numbered choice.");continue
        try:state=select(story,state,int(choice)-1)
        except ValueError:print("Choice not available.")
def main():
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo",action="store_true");mode.add_argument("--play",action="store_true")
    a=p.parse_args()
    story=json.loads(STORY.read_text(encoding="utf-8"))
    if a.demo:print(json.dumps(demo(story),indent=2))
    else:play(story)
if __name__=="__main__":main()
