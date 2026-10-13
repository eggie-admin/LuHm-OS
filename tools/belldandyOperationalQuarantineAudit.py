#!/usr/bin/env python3
"""Evidence-only quarantine regression. No mutations."""
import json
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
policy=json.loads((root/"doctrine/belldandyOperationalQuarantineV1.json").read_text())
company=json.loads((root/"doctrine/companyWideOperationalQuarantineV1.json").read_text())
company_held=company.get("state")=="QUARANTINED"
assert policy["schema"]=="luhmOs.belldandyOperationalQuarantine.v1"
assert policy["subject"]=="belldandySecretary"
assert policy["state"]=="QUARANTINED"
assert policy["release"]["professorApprovalReceipt"] is None
for kind,expected in [("records",["lum","fumi"]),("dictation",["lum","koe"]),("monitor",["lum","urdDoctorGoddess","skuldResearch"]),("release",["lum","urdDoctorGoddess","ProfessorCrown"])]:
    p=subprocess.run([sys.executable,str(root/"tools/lumTaskRouter.py"),kind],cwd=root,text=True,capture_output=True,check=True)
    result=json.loads(p.stdout)
    assert result["workers"]==([] if company_held else expected), (kind,result["workers"])
    assert result["operationalQuarantine"]["state"]=="QUARANTINED"
    assert "belldandySecretary" not in result["workers"]
    assert "belldandySecretary" in result["residentCabinet"]
    assert "belldandySecretary" not in result["activeResidentCabinet"]
    if company_held:
        assert result["activeResidentCabinet"] == []
        assert result["companyQuarantine"]["activeWorkers"] == 0
    assert result["greenAuthority"] is False
print("GREEN_BELLDANDY_QUARANTINE_ROUTING_SOURCE_ONLY")
