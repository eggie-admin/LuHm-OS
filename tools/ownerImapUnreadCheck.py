#!/usr/bin/env python3
"""Opt-in, read-only remote IMAP unread-count check. Never fetches mail bodies."""
import argparse
import imaplib
import json
import os
import re
import ssl

DOMAIN = re.compile(r"^[a-zA-Z0-9.-]{4,253}$")

def check_unread(host,user,token,*,client_factory=imaplib.IMAP4_SSL):
    if not DOMAIN.fullmatch(host) or "." not in host or not user or not token:
        raise ValueError("IMAP_CONFIG_MISSING_OR_INVALID")
    conn=client_factory(host,993,ssl_context=ssl.create_default_context(),timeout=10)
    try:
        auth_bytes=("user="+user+"\x01auth=Bearer "+token+"\x01\x01").encode("utf-8")
        result,_=conn.authenticate("XOAUTH2",lambda challenge:auth_bytes)
        if result!="OK":raise ValueError("IMAP_AUTH_REJECTED")
        result,_=conn.select("INBOX",readonly=True)
        if result!="OK":raise ValueError("IMAP_READONLY_SELECT_REJECTED")
        result,ids=conn.search(None,"UNSEEN")
        if result!="OK":raise ValueError("IMAP_SEARCH_REJECTED")
        unread=len(ids[0].split()) if ids and ids[0] else 0
        return {"schema":"luhmOs.imapUnreadReceipt.v1","readOnly":True,
                "unreadCount":unread,"bodyFetched":False,"mailMutated":False,
                "emailAddressesReturned":False,"crownStatus":"STOP"}
    finally:
        try:conn.logout()
        except OSError:pass

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true",help="Manually connect to approved IMAP host")
    args=parser.parse_args()
    if not args.check:
        print(json.dumps({"schema":"luhmOs.imapUnreadReceipt.v1","mode":"DRY_RUN",
           "networkCalled":False,"mailboxConnected":False,"crownStatus":"STOP"}))
        return
    host=os.environ.get("LUHM_IMAP_HOST","")
    user=os.environ.get("LUHM_IMAP_USER","")
    token=os.environ.get("LUHM_IMAP_OAUTH_TOKEN","")
    if not host or not user or not token:
        parser.error("explicit IMAP host/user OAuth2 environment required")
    print(json.dumps(check_unread(host,user,token)))

if __name__=="__main__":
    main()
