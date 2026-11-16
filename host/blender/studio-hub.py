"""Local-only LuHm studio hub for Blender's native editors and installed desktop tools.

The operator controls never install packages, run arbitrary shell strings, touch
private art files, deploy services, or grant agent/Crown authority.
"""
from pathlib import Path
import os
import shutil
import subprocess
import webbrowser

import bpy
from bpy.props import StringProperty


ROOT = Path(__file__).resolve().parents[2]
WORKSPACES = (
    ("Layout", "3D Layout"),
    ("Modeling", "Modeling"),
    ("Sculpting", "Sculpting"),
    ("UV Editing", "UV Editing"),
    ("Texture Paint", "Texture Paint"),
    ("Shading", "Materials / Shading"),
    ("Animation", "Animation"),
    ("Rendering", "Rendering"),
    ("Compositing", "Compositing"),
    ("Geometry Nodes", "Geometry Nodes"),
    ("Scripting", "Python / Scripting"),
    ("Video Editing", "Video Editor"),
)
EDITABLE_SCRIPTS = {
    "cockpit": ROOT / "host/blender/luhm-cockpit.py",
    "studio": ROOT / "host/blender/studio-hub.py",
    "handoff": ROOT / "host/blender/blender-godot-handoff.py",
}
DOC_SOURCES = {
    "blender": "https://docs.blender.org/manual/en/latest/",
    "extensions": "https://extensions.blender.org/",
    "godot": "https://docs.godotengine.org/en/stable/",
}


def choose_launch(tool):
    """Fixed argv, no shell expansion, providers, package changes, or downloads."""
    if tool == "ide":
        for name in ("code", "codium"):
            binary = shutil.which(name)
            if binary:
                return [binary, "--new-window", str(ROOT)]
        raise FileNotFoundError("VS Code or VSCodium is not installed")
    if tool == "godot":
        binary = shutil.which("godot")
        if binary:
            return [binary, "--editor", "--path", str(ROOT)]
        raise FileNotFoundError("Godot executable is not installed")
    if tool == "gimp":
        binary = shutil.which("gimp")
        if binary:
            return [binary]
        raise FileNotFoundError("GIMP executable is not installed")
    if tool == "terminal":
        binary = shutil.which("xterm")
        if binary and Path("/bin/bash").is_file():
            return [binary, "-e", "/bin/bash", "-l"]
        raise FileNotFoundError("xterm and /bin/bash are required for the terminal")
    raise ValueError("Unapproved tool key")


class LUHM_OT_studio_workspace(bpy.types.Operator):
    bl_idname = "luhm.studio_workspace"
    bl_label = "Switch Studio Workspace"
    bl_description = "Use a native Blender workspace; no file or service changes"

    workspace_name: StringProperty(name="Workspace")

    def execute(self, context):
        allowed = {name for name, _ in WORKSPACES}
        if self.workspace_name not in allowed:
            self.report({"WARNING"}, "Unknown studio workspace")
            return {"CANCELLED"}
        workspace = bpy.data.workspaces.get(self.workspace_name)
        if workspace is not None and context.window is not None:
            context.window.workspace = workspace
            return {"FINISHED"}
        # Startup files may omit these workspaces; the native editor still exists.
        fallback = {"Video Editing": "SEQUENCE_EDITOR", "Scripting": "TEXT_EDITOR"}
        area_type = fallback.get(self.workspace_name)
        if area_type is not None and context.area is not None:
            context.area.type = area_type
            self.report({"INFO"}, "Native editor opened. Shift-F5 returns to 3D View.")
            return {"FINISHED"}
        self.report({"WARNING"}, "Workspace unavailable in this Blender session")
        return {"CANCELLED"}


class LUHM_OT_studio_script(bpy.types.Operator):
    bl_idname = "luhm.studio_script"
    bl_label = "Open Studio Python"
    bl_description = "Load known local source as editable text; do not execute it"

    script_key: StringProperty(name="Local Script")

    def execute(self, context):
        script_path = EDITABLE_SCRIPTS.get(self.script_key)
        if script_path is None or not script_path.is_file():
            self.report({"WARNING"}, "Script unavailable")
            return {"CANCELLED"}
        # A Text Editor data-block is not executable by opening it.
        text = bpy.data.texts.load(filepath=str(script_path), internal=False, check_existing=True)
        workspace = bpy.data.workspaces.get("Scripting")
        if workspace is not None and context.window is not None:
            context.window.workspace = workspace
        screen = context.window.screen if context.window else context.screen
        if screen is not None:
            for area in screen.areas:
                if area.type == "TEXT_EDITOR":
                    area.spaces.active.text = text
                    break
        self.report({"INFO"}, "Opened for editing only: " + script_path.name)
        return {"FINISHED"}


class LUHM_OT_studio_launch(bpy.types.Operator):
    bl_idname = "luhm.studio_launch"
    bl_label = "Open Local Tool"
    bl_description = "Explicit desktop launch of an already installed tool"

    tool_key: StringProperty(name="Installed Tool")

    def execute(self, context):
        try:
            if os.name == "posix" and not (
                os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
            ):
                raise RuntimeError("No graphical desktop session attached")
            argv = choose_launch(self.tool_key)
            subprocess.Popen(
                argv, cwd=str(ROOT), stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                close_fds=True, start_new_session=True,
            )
        except (ValueError, RuntimeError, OSError) as exc:
            self.report({"WARNING"}, str(exc)[:180])
            return {"CANCELLED"}
        self.report({"INFO"}, "Opened installed desktop tool: " + self.tool_key)
        return {"FINISHED"}


class LUHM_OT_studio_extensions(bpy.types.Operator):
    bl_idname = "luhm.studio_extensions"
    bl_label = "Review Blender Extensions"
    bl_description = "Open Blender's native preferences; never auto-install add-ons"

    def execute(self, context):
        if bpy.app.background:
            self.report({"WARNING"}, "Extension manager requires a Blender GUI")
            return {"CANCELLED"}
        try:
            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        except RuntimeError as exc:
            self.report({"WARNING"}, str(exc)[:180])
            return {"CANCELLED"}
        return {"FINISHED"}


class LUHM_OT_studio_docs(bpy.types.Operator):
    bl_idname = "luhm.studio_docs"
    bl_label = "Open Documentation"
    bl_description = "Open a fixed official docs URL only when clicked"

    source_key: StringProperty(name="Documentation Source")

    def execute(self, context):
        address = DOC_SOURCES.get(self.source_key)
        if address is None:
            return {"CANCELLED"}
        if bpy.app.background:
            self.report({"WARNING"}, "Documentation browser requires a GUI")
            return {"CANCELLED"}
        if not webbrowser.open(address):
            self.report({"WARNING"}, "Default browser could not open documentation")
            return {"CANCELLED"}
        return {"FINISHED"}


class LUHM_PT_studio_workspaces(bpy.types.Panel):
    bl_label = "Studio Workspaces"
    bl_idname = "LUHM_PT_studio_workspaces"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LuHm"
    bl_parent_id = "LUHM_PT_cockpit"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Blender-native workspaces")
        for name, title in WORKSPACES:
            layout.operator("luhm.studio_workspace", text=title).workspace_name = name


class LUHM_PT_studio_code(bpy.types.Panel):
    bl_label = "Python + IDE + Terminal"
    bl_idname = "LUHM_PT_studio_code"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LuHm"
    bl_parent_id = "LUHM_PT_cockpit"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        for key, label in (
            ("cockpit", "Edit Cockpit Python"),
            ("studio", "Edit Studio Hub Python"),
            ("handoff", "Edit Godot Handoff Python"),
        ):
            layout.operator("luhm.studio_script", text=label).script_key = key
        layout.separator()
        layout.label(text="Installed desktop applications")
        for key, label in (
            ("ide", "Launch VS Code / VSCodium"),
            ("terminal", "Launch Local Terminal"),
            ("godot", "Launch Godot Editor"),
            ("gimp", "Launch GIMP"),
        ):
            layout.operator("luhm.studio_launch", text=label).tool_key = key
        layout.label(text="Python Console: Scripting workspace")


class LUHM_PT_studio_media(bpy.types.Panel):
    bl_label = "Video + Animation"
    bl_idname = "LUHM_PT_studio_media"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LuHm"
    bl_parent_id = "LUHM_PT_cockpit"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        for name, title in (
            ("Video Editing", "Open Video Sequence Editor"),
            ("Animation", "Open Character Animation"),
            ("Compositing", "Open Node Compositor"),
            ("Rendering", "Open Render Workspace"),
        ):
            layout.operator("luhm.studio_workspace", text=title).workspace_name = name
        layout.label(text="Media rendering remains explicit")


class LUHM_PT_studio_community(bpy.types.Panel):
    bl_label = "Community + Plugins"
    bl_idname = "LUHM_PT_studio_community"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LuHm"
    bl_parent_id = "LUHM_PT_cockpit"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("luhm.studio_extensions", text="Review Installed Extensions")
        for key, title in (
            ("extensions", "Blender Community Extensions"),
            ("blender", "Official Blender Manual"),
            ("godot", "Godot Documentation"),
        ):
            layout.operator("luhm.studio_docs", text=title).source_key = key
        layout.separator()
        layout.label(text="No automatic downloads or installs")
        layout.label(text="Quarantine + provenance before reuse")


CLASSES = (
    LUHM_OT_studio_workspace, LUHM_OT_studio_script,
    LUHM_OT_studio_launch, LUHM_OT_studio_extensions, LUHM_OT_studio_docs,
    LUHM_PT_studio_workspaces, LUHM_PT_studio_code,
    LUHM_PT_studio_media, LUHM_PT_studio_community,
)
