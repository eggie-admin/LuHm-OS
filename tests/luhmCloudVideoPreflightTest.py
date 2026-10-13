"""No-network read-only Cloud probe negative controls."""
import importlib.util
import json
import pathlib
import subprocess
import sys
root = pathlib.Path(__file__).resolve().parents[1]
path = root / "host/api/luhmCloudVideoPreflight.py"
spec = importlib.util.spec_from_file_location("preflight", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
projectId = "test-project-123"
calls = []
def fakeGet(url):
    calls.append(url)
    if "cloudbilling.googleapis.com" in url:
        return {"projectId": projectId, "billingEnabled": True}
    return {"name":"projects/"+projectId+"/services/aiplatform.googleapis.com","state":"ENABLED"}
report = module.probe(projectId, fakeGet)
assert len(calls) == 2 and all(url.startswith("https://") for url in calls)
assert report["billing"] == "ENABLED" and report["vertexApi"] == "ENABLED"
assert report["readyToSpend"] is False and report["crown"] == "STOP"
assert report["iam"] == "UNVERIFIED" and report["quota"] == "UNVERIFIED"
disabled = module.probe(projectId, lambda url: {"projectId":projectId,"billingEnabled":False} if "cloudbilling" in url else {"name":"projects/"+projectId+"/services/aiplatform.googleapis.com","state":"DISABLED"})
assert disabled["billing"] == "DISABLED" and disabled["vertexApi"] == "DISABLED"
bad = module.probe(projectId, lambda url: {"billingEnabled": True,"state":"ENABLED"})
assert bad["billing"] == "INVALID_PROVIDER_RESPONSE"
assert bad["vertexApi"] == "INVALID_PROVIDER_RESPONSE"
try:
    module.probe("evil.example/path",fakeGet)
    raise AssertionError("Invalid project accepted")
except ValueError:
    pass
dry = subprocess.run([sys.executable,str(path)],text=True,capture_output=True,check=True)
assert json.loads(dry.stdout)["mode"] == "OFFLINE_NO_REQUESTS"
assert json.loads(dry.stdout)["readyToSpend"] is False
print("YUME_READ_ONLY_CLOUD_PREFLIGHT_GREEN")
