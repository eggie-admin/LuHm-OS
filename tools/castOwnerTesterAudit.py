#!/usr/bin/env python3
"""Fail closed: an updated personal Site skill is not the public tester's ChatGPT app."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"doctrine/castOwnerTesterActivationV1.json"

def check(d):
    bad=[]
    def require(v,code):
        if not v: bad.append(code)
    require(d.get("schema")=="luhmOs.castOwnerTesterActivation.v1","SCHEMA")
    require(d.get("crownStatus")=="STOP","CROWN")
    own=d.get("ownership",{})
    require(own.get("sitePluginScope")=="USER" and own.get("sitePluginAudience")=="PRIVATE","SITE_SCOPE")
    require(own.get("siteAppBindingMustBePreserved") is True and own.get("independentVersionStreams") is True,"SITE_IDENTITY")
    auth=d.get("operatorMode",{})
    require(auth.get("safeTasksAutoAuthorized") is True and auth.get("noRoutineApprovalLoops") is True,"AUTOMATION")
    require(auth.get("noDuplicateSiteApps") is True and auth.get("noAutonomousAgentElevation") is True,"NO_PRIVILEGE_ESCALATION")
    cast=d.get("cast",{})
    require(cast.get("ownerChatGptAndroidInlineMount")=="RED_SOMETHING_WENT_WRONG_SCREENSHOT_OBSERVED","OWNER_DISPLAY")
    require(cast.get("failedHostMountOverridesCiSuccess") is True and cast.get("noBlindRetry") is True,"NO_FALSE_GREEN")
    require(cast.get("currentSiteBackendEditor")=="NOT_EXPOSED_BY_CONNECTED_TOOLS","SITE_BACKEND_LIMIT")
    access=d.get("access",{})
    require(access.get("owner",{}).get("status")=="PLUGIN_INSTALLED_BUT_GUI_RED","OWNER_READY_FALSE")
    tester=access.get("firstTester",{})
    require(tester.get("status")=="NO_INDEPENDENT_CHATGPT_ACCESS_PROVED","TESTER_READY_FALSE")
    require(tester.get("privateUserPluginShareableByLink") is False,"PRIVATE_NOT_SHAREABLE")
    require(tester.get("sendInviteAutomatically") is False,"NO_UNAPPROVED_INVITE")
    require("supportedSharedWorkspacePluginAndSiteViewerPermission" in tester.get("acceptableDistribution",[]),"WORKSPACE_ROUTE")
    require("separatelyReviewedApprovedReadOnlyPublicDirectoryApp" in tester.get("acceptableDistribution",[]),"PUBLIC_REVIEW_ROUTE")
    require([x.get("id") for x in d.get("releaseGates",[])]==["source","host","owner","tester"],"GATE_ORDER")
    require(d.get("releaseTrain")==["testing","proposed","beta","betaLts"],"FOUR_RELEASE_LANES")
    require(d.get("providerLimits",{}).get("pluginCreatorEditsSkillsNotSiteBackend") is True,"NO_SKILL_MOUNT_CLAIM")
    require(d.get("assets",{}).get("doNotExposePrivateDrive") is True,"PRIVATE_ASSETS")
    return bad

if __name__=="__main__":
    p=json.loads(DOC.read_text(encoding="utf-8"))
    errors=check(p)
    if errors:
        print("RED_CAST_OWNER_TESTER "+",".join(errors))
        raise SystemExit(1)
    print("GREEN_CAST_OWNER_TESTER_DOCTRINE_SOURCE_ONLY")
    print("OWNER_IN_CHAT_GUI=RED; TESTER_ACCESS=BLOCKED; SITE_PLUGIN_SKILL_RELEASE=SEPARATE_ACCOUNT_EVIDENCE")
    print("CROWN=STOP")
