"""LuHm local Blender cockpit. Load in Blender's Text Editor and Run Script."""
import json
from pathlib import Path
import shutil
import subprocess
import bpy

bl_info = {"name": "LuHm Artist Cockpit", "version": (0, 1, 0),
           "blender": (3, 6, 0), "category": "3D View"}
ROOT = Path(__file__).resolve().parents[2]
STATUS = "Ready. Local tools only."
TOOLS = ("python3", "ffmpeg", "godot", "mariadb")

def run_local(argv, timeout=15):
    """Fixed argument arrays only; no shell, credentials or service startup."""
    result = subprocess.run(argv, cwd=str(ROOT), capture_output=True,
                            text=True, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError("Local command failed (exit %s)" % result.returncode)
    return result.stdout.strip()[:300]

class LUHM_OT_check(bpy.types.Operator):
    bl_idname = "luhm.check_local"
    bl_label = "Check Local Tools"
    def execute(self, context):
        global STATUS
        STATUS = "; ".join(tool + ": " + ("found" if shutil.which(tool) else "missing")
                           for tool in TOOLS)
        self.report({"INFO"}, STATUS)
        return {"FINISHED"}

class LUHM_OT_database(bpy.types.Operator):
    bl_idname = "luhm.check_database"
    bl_label = "Probe Local MariaDB"
    def execute(self, context):
        global STATUS
        try:
            # Read-only query; never fall back to TCP, start DB or elevate.
            value = run_local(["mariadb", "--no-defaults", "--protocol=SOCKET",
                "--socket=/run/mysqld/mysqld.sock", "--connect-timeout=3",
                "--batch", "--skip-column-names", "--execute=SELECT 1"])
            if value != "1":
                raise RuntimeError("Unexpected database reply")
            STATUS = "MariaDB: local socket SELECT 1 passed."
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            STATUS = "MariaDB unavailable: start/configure the local socket service explicitly."
            self.report({"WARNING"}, STATUS)
            return {"CANCELLED"}
        self.report({"INFO"}, STATUS)
        return {"FINISHED"}

class LUHM_OT_godot(bpy.types.Operator):
    bl_idname = "luhm.check_godot"
    bl_label = "Check Godot Handoff"
    def execute(self, context):
        global STATUS
        try:
            project = ROOT / "project.godot"
            if not project.is_file():
                raise RuntimeError("Missing project.godot")
            version = run_local(["godot", "--headless", "--version"])
            if not version.startswith("4."):
                raise RuntimeError("Godot 4 required")
            STATUS = "Godot 4 found; project exists. Import/play not yet tested."
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            STATUS = "Godot 4/project unavailable."
            self.report({"WARNING"}, STATUS)
            return {"CANCELLED"}
        self.report({"INFO"}, STATUS)
        return {"FINISHED"}

class LUHM_PT_cockpit(bpy.types.Panel):
    bl_label = "LuHm Artist Cockpit"
    bl_idname = "LUHM_PT_cockpit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LuHm"
    def draw(self, context):
        layout = self.layout
        layout.label(text="Professor's local art desk")
        layout.operator("luhm.check_local")
        layout.operator("luhm.check_database")
        layout.operator("luhm.check_godot")
        layout.separator()
        layout.label(text=STATUS)
        layout.label(text="Save masters with Blender Save As.")
        layout.label(text="Runtime/device acceptance pending.")

CLASSES = (LUHM_OT_check, LUHM_OT_database, LUHM_OT_godot, LUHM_PT_cockpit)

def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

def selftest():
    """Actual Blender registration/operator smoke; no assets/network/DB required."""
    register()
    try:
        assert (ROOT / "project.godot").is_file()
        assert bpy.ops.luhm.check_local() == {"FINISHED"}
        assert bpy.types.LUHM_PT_cockpit.bl_category == "LuHm"
        print(json.dumps({"test": "blender-cockpit-registration",
                          "blender": bpy.app.version_string,
                          "result": "PASS", "interactiveTouch": "UNVERIFIED"}))
    finally:
        unregister()
    register()
    unregister()

if __name__ == "__main__":
    import sys
    if "--luhm-selftest" in sys.argv:
        selftest()
    else:
        register()
