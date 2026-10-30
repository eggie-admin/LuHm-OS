#!/usr/bin/env python3
"""Fail-closed source-only hardware/vendor/headless doctrine checks."""
import ast
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[1]

def evaluate(hardware,surface,source,canon,quarantine,backendSource):
    checks={}
    def check(name,result): checks[name]=bool(result)
    devices=hardware.get("inventory",[])
    ids=[d.get("id") for d in devices]
    check("hardwareSchema",hardware.get("schema")=="luhmOs.k9000UniversalHardware.v1")
    check("vendorSchema",surface.get("schema")=="luhmOs.k9000UniversalVendorSurface.v1")
    check("tenDevices",len(devices)>=10 and len(ids)==len(set(ids)))
    check("yetiPending",any(x.get("id")=="yetiMicrophone" and x.get("observed")=="USER_REPORTED_THIS_TURN" and not x.get("verifiedRuntime") for x in devices))
    check("bluetoothJackPending",any(x.get("id")=="bluetoothAudioJack" and "unknown" in x.get("model","").lower() and not x.get("verifiedRuntime") for x in devices))
    check("privateIdsExcluded",hardware.get("privateDocumentIdsExcluded") is True)
    check("noDriverPretend",all(d.get("verifiedRuntime") is False for d in devices))
    check("noKernelMutation",hardware.get("autoModifyKernel") is False and hardware.get("autoInstallDrivers") is False)
    check("noBluetoothAutoPair",hardware.get("autoPairBluetooth") is False)
    check("noAutoRecording",hardware.get("autoStartCapture") is False)
    check("noSerialExfil",hardware.get("autoExposeSerials") is False)
    check("noGpartedBrowser",hardware.get("gparted")=="HOST_OPERATOR_ONLY_NO_WEBVIEW_PARTITION_WRITES")
    check("linuxHostUnmodified","no host OS migration" in hardware["targetPlatforms"]["linux"]["currentStudio"].lower())
    check("ubuntuLtsTarget","26.04.1 LTS" in hardware["targetPlatforms"]["linux"]["hostBaseline"])
    check("iOSBuildHonest","macOS + Xcode" in hardware["targetPlatforms"]["ios"]["buildRequirement"])
    check("noFakeIphone",hardware["targetPlatforms"]["ios"]["deviceInventory"]=="NO_OWNER_IPHONE_CONFIRMED")
    check("stockAndroid",hardware["targetPlatforms"]["android"]["vendorKernelPreserved"] is True)
    check("headlessCore",surface["oneApp"]["backend"]=="Python3 stdlib loopback capability core")
    check("sqliteLocal",surface["oneApp"]["database"]=="SQLite3 parameterized local-only")
    check("noBrowserSql",surface["oneApp"]["noDirectBrowserSql"] is True)
    check("providerCatalog",set(surface["vendors"]["google"]["catalog"])=={"gmail","docs","drive","cloud","gemini","playStore","edgeGallery","liteRtLm"})
    check("gmailNotAutoAuth",surface["vendors"]["google"]["catalog"]["gmail"]["readiness"]=="NOT_CONNECTED_TO_APP")
    check("geminiNotAutoAuth",surface["vendors"]["google"]["catalog"]["gemini"]["readiness"]=="UNVERIFIED")
    check("edgeGalleryNotServer",surface["vendors"]["google"]["catalog"]["edgeGallery"]["readiness"]=="REFERENCE_ONLY")
    check("openAiOptional",surface["vendors"]["openAi"]["mustNotBeBrowserDependency"] is True)
    check("oldCanonPrecedencePreserved",source["activeCompatibilityOrder"]["first"]=="chatGptOpenAi" and
          surface["priority"]["changeToPrimaryOrder"]=="PROPOSED_CONFLICT_PENDING_PROFESSOR_CROWN")
    check("llamaNotBundled",surface["models"]["llama"]["fDroidDistribution"] is False and
          surface["models"]["defaultModelBundled"] is False)
    check("noModelAutoDownload",surface["models"]["noAutoDownload"] is True)
    check("companyQuarantine",quarantine["state"]=="QUARANTINED" and quarantine["activeTaskWorkersAllowed"] is False)
    check("crownStop",surface["security"]["crownStatus"]=="STOP" and canon["gates"]["humanPromotion"] is False)
    check("noPublicBind",surface["security"]["hostBind"]=="127.0.0.1" and surface["security"]["noWildcardBind"] is True)
    check("noHeadlessCloudDependency","cloudAuth" in surface["oneApp"]["headlessMustNeverNeed"])
    check("noHeadlessDisplayDependency","displayServer" in surface["oneApp"]["headlessMustNeverNeed"])
    check("canonicalLayerColumns",surface["architecture"]["columns"]==["coreLibrary","pluginExtension","classWidgetOrganization","stubAdapterBoundary"])
    check("canonicalRhythm",surface["architecture"]["rhythm"]==["hear","resolve","act","verify"])
    check("canonicalEscalation",surface["architecture"]["escalation"]==[0,1,2,3])
    check("backendPythonParse",isinstance(ast.parse(backendSource),ast.Module))
    check("noHTTPPost",'"READ_ONLY_NO_MUTATIONS"' in backendSource and "def do_POST" in backendSource)
    check("noGenericBinding",'host != "127.0.0.1"' in backendSource)
    check("noShellCommands","subprocess" not in backendSource and "os.system" not in backendSource)
    check("noSQLDynamicEndpoint",'"/v1/sql"' not in backendSource and '":memory:"' in backendSource)
    check("noRootPrivilege","allow_reuse_address" in backendSource and "os.setuid" not in backendSource)
    return checks

def audit():
    def obj(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
    hw=obj("doctrine/k9000UniversalHardwareV1.json")
    vendors=obj("doctrine/k9000UniversalVendorSurfaceV1.json")
    src=obj("doctrine/currentSourceTruthV3.json")
    canon=obj("doctrine/k9000CrownCathedralReleaseV1.json")
    hold=obj("doctrine/companyWideOperationalQuarantineV1.json")
    backend=(ROOT/"host/api/k9000HeadlessCore.py").read_text(encoding="utf-8")
    checks=evaluate(hw,vendors,src,canon,hold,backend)
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE audit_receipt(id TEXT PRIMARY KEY NOT NULL,state TEXT NOT NULL CHECK(state IN ('PASS','FAIL')))")
        db.execute("INSERT INTO audit_receipt VALUES (?,?)",("source","PASS"))
        sqlOk=db.execute("SELECT state FROM audit_receipt WHERE id=?",("source",)).fetchone()==("PASS",)
        try:
            db.execute("INSERT INTO audit_receipt VALUES (?,?)",("bad","UNVERIFIED"))
            sqlOk=False
        except sqlite3.IntegrityError:
            pass
    checks["sqliteParameterizedCheckConstraint"]=sqlOk
    failed=[k for k,v in checks.items() if not v]
    return {"schema":"luhmOs.k9000UniversalHardwareAudit.v1",
            "sourceChecks":len(checks),"passed":len(checks)-len(failed),"failed":failed,
            "verdict":"SOURCE_GREEN_ONLY" if not failed else "RED_SOURCE",
            "driverRuntime":"UNVERIFIED","iosRuntime":"UNVERIFIED",
            "googleConnected":"NOT_PROVEN_IN_APP","openAiLive":"NOT_PROVEN",
            "crownStatus":"STOP"}

if __name__=="__main__":
    r=audit()
    print(json.dumps(r,indent=2))
    if r["failed"]:raise SystemExit(1)
