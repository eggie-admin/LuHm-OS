#!/usr/bin/env python3
"""Build an offline NONSECRET, read-only-ready studio registry from public GitHub receipts.

The file is NOT a credential vault, not a signing authority, and not a production DB.
"""
import argparse
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"host/api/studioRegistrySqliteV1.sql"
CANON=ROOT/"doctrine/studioFinalBossControlV1.json"
RECEIPT=ROOT/"campaign/instagramReturn20261115Receipt.json"

def build(output:Path)->dict:
    cfg=json.loads(CANON.read_text(encoding="utf-8"))
    pub=json.loads(RECEIPT.read_text(encoding="utf-8"))
    if cfg["publicDomain"]!="eggiebagelface.art":raise ValueError("wrong domain")
    if pub["verification"]!="INDEPENDENT_WINDSOR_READBACK_MEDIA_ID_CAPTION_AND_PERMALINK_MATCH":
        raise ValueError("publication verification missing")
    if pub["mediaId"]!=cfg["verifiedSocial"]["instagram"]["postId"]:
        raise ValueError("social receipt mismatch")
    if output.exists():raise FileExistsError("Refusing to overwrite existing registry snapshot")
    output.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(output)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        # Immutable canonical source hash of the independently verified Instagram asset.
        anchor=pub["sourceCommit"]
        for b in cfg["brands"]:
            conn.execute("INSERT INTO brand VALUES (?,?,?,?,?)",
              (b["id"],b["name"],b["role"],int(b["legalEntityProof"]),anchor))
        lanes=[
          ("privateMutation","private",0,"Originals and experiments never public"),
          ("proposedInvite","inviteOnly",0,"Private candidate branches and explicit testers"),
          ("betaAfterDark","inviteOnly",0,"Private mature art beta per existing Canon"),
          ("publicBeta","public",1,"Sanitized beta source only, signed distribution after tests"),
          ("cathedralPublic","public",1,"Public-safe assets require explicit release proofs"),
          ("ltsPublic","public",1,"Long-term supported and signed updates after hardware and rollback proof")
        ]
        conn.executemany("INSERT INTO release_lane VALUES (?,?,?,?,?)",[(a,b,c,1,d) for a,b,c,d in lanes])
        conn.execute("INSERT INTO social_account VALUES (?,?,?,?,?)",
                     ("instagram","eggiebagelface","eggieBagelfaceArt","Windsor.ai",1))
        conn.execute("INSERT INTO social_release VALUES (?,?,?,?,?,?,?)",(
            pub["platform"],pub["mediaId"],pub["brand"],pub["permalink"],
            pub["sourceCommit"],"campaign/instagramReturn20261115Receipt.json",
            pub["publishedAtUtc"]))
        for idx,(p,state) in enumerate([
          ("deterministicLocal","verified"),("googleGeminiFlashLite","unverified"),
          ("openAiPremium","unverified")]):
            conn.execute("INSERT INTO provider_route VALUES (?,?,?,?,?,?,?)",(
                p,"inferenceOrLocal",state,"ownerEncryptedVault" if idx else "notProvisioned",
                0,idx+1,"No external billable calls. Eligibility requires per-account receipt."))
        for vendor,purpose in [
            ("githubGpg","ownerGitCommitAndTag"),
            ("googlePlayAppSigning","AndroidApp"),
            ("appleDeveloperSigning","iOSDistribution"),
            ("samsungKnox","SamsungEnterpriseDistribution"),
            ("androidOtaFirmware","OSFirmwareUpdates"),
            ("letsEncrypt","PublicHTTPS")
        ]:
            conn.execute("INSERT INTO signing_enrollment VALUES (?,?,?,?,?,?,?)",(
                vendor,purpose,"unverified",None,"notProvisioned",None,None))
        conn.execute("INSERT INTO task_receipt VALUES (?,?,?,?,?,?,?,?)",(
            "public-ig-20261115",pub["sourceCommit"],"publishStudioComeback",
            "deterministicLocal","verified","Professor",pub["permalink"],pub["publishedAtUtc"]))
        conn.commit()
        return {k:conn.execute("SELECT COUNT(*) FROM "+k).fetchone()[0] for k in
                ("brand","release_lane","social_account","social_release","provider_route","signing_enrollment","task_receipt")}
    except Exception:
        conn.close()
        output.unlink(missing_ok=True)
        raise
    finally:
        try:conn.close()
        except Exception:pass

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path,help="New PRIVATE local .sqlite3 path; refuses overwrite")
    args=p.parse_args()
    result=build(args.output.expanduser().resolve())
    print(json.dumps({"result":"CREATED_NONSECRET_INDEX","output":str(args.output),"counts":result},sort_keys=True))
if __name__=="__main__":main()
