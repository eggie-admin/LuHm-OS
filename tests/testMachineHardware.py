import importlib.util,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S=importlib.util.spec_from_file_location("hardwareProbe",ROOT/"tools/machineHardwareProbe.py")
mod=importlib.util.module_from_spec(S);S.loader.exec_module(mod)
class MachineHardwareTests(unittest.TestCase):
 def test_reports_tools_not_devices(self):
  x=mod.snapshot(which=lambda name: "/mock/bin/"+name if name=="vulkaninfo" else None,system=lambda:"Linux",machine=lambda:"aarch64")
  self.assertTrue(x["toolAvailabilityOnly"]["gpuVulkan"])
  self.assertFalse(x["toolAvailabilityOnly"]["gpuNvidia"])
  for prop in ("firmwareFlashed","kernelModified","deviceConnectedProof","graphicsRuntimeProof","deviceIdsRecorded"):
   self.assertIs(x[prop],False)
 def test_boss_plugin_contract_cannot_force_host(self):
  x=json.loads((ROOT/"doctrine/luhmPluginDefaultBoss20261114V1.json").read_text())
  self.assertEqual(x["product"],"LuHm-OS")
  self.assertEqual(x["canonicalBoss"],"lum")
  self.assertFalse(x["hostAutopopupGuaranteed"])
  self.assertEqual(x["agentRuntime"],"COMPANY_WIDE_QUARANTINE")
