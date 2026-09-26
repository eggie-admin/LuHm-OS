"""Run Godot smoke tests with error-log and timeout enforcement."""
import re
import subprocess
import sys

MARKERS = {
    "communityAssetsSmoke": "COMMUNITY ASSETS SMOKE PASS",
    "layoutSmoke": "SAMSUNG ORIENTATION HARNESS PASS",
    "runtimeSmoke": "CROWN RUNTIME SMOKE GREEN",
    "lumRigV2Phase1Smoke": "LUHM RIG V2 PHASE 1 GREEN",
}

def validate(output, returncode, marker):
    if returncode != 0 or re.search(r"(?:SCRIPT ERROR:|ERROR:|Parse Error:)", output):
        raise ValueError("Godot smoke failed or logged an engine/script error")
    if marker not in output:
        raise ValueError("Godot smoke completion marker missing")

if __name__ == "__main__":
    binary, name = sys.argv[1:]
    marker = MARKERS[name]
    result = subprocess.run(
        [binary, "--headless", "--path", ".", "--script", f"res://tests/{name}.gd"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=90,
    )
    print(result.stdout, end="")
    validate(result.stdout, result.returncode, marker)
