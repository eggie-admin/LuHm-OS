import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import asyncio

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("antennaHost", ROOT / "host/mcp/luhmAntenna.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class Registry:
    def __init__(self):
        self.tools = {}
        self.resources = {}

    def tool(self, **meta):
        def register(fn):
            self.tools[meta["name"]] = (fn, meta)
            return fn
        return register

    def resource(self, uri, **meta):
        def register(fn):
            self.resources[uri] = (fn, meta)
            return fn
        return register


class HostTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "doctrine").mkdir()
        (self.root / "tools").mkdir()
        (self.root / "doctrine/samsungAntennaV1.json").write_text(json.dumps({"schema": "luhmOs.samsungAntenna.v1"}))
        shutil.copyfile(ROOT / "tools/kai9000Antenna.py", self.root / "tools/kai9000Antenna.py")
        self.server = Registry()
        app.register_antenna(self.server, root=self.root, annotations={"readOnlyHint": True})

    def tearDown(self):
        self.temp.cleanup()

    def test_tools_and_widget_are_additive_and_request_only(self):
        fn, meta = self.server.tools["luhm_open_antenna"]
        result = fn()
        self.assertFalse(result["executionEnabled"])
        self.assertFalse(result["phoneConnectionProven"])
        self.assertEqual(result["gameWork"], "onHold")
        self.assertEqual(len(result["services"]), 10)
        self.assertEqual(meta["meta"]["ui"]["resourceUri"], app.URI)
        self.assertEqual(self.server.resources[app.URI][1]["mime_type"], "text/html;profile=mcp-app")

    def test_shared_python_animation_plan(self):
        fn, _ = self.server.tools["luhm_plan_antenna_creation"]
        result = fn("characterAnimation", "remoteStudio", "Original character dance")
        self.assertEqual(result["animationPipeline"]["godotRole"], "characterAnimationOnly")
        self.assertFalse(result["aiInvoked"])
        self.assertFalse(result["executionEnabled"])
        with self.assertRaises(ValueError):
            fn("executeCode", "remoteStudio", "bad")

    def test_resource_budget_and_missing_build_fallback(self):
        fn, _ = self.server.resources[app.URI]
        self.assertIn("build pending", fn())
        bundle = self.root / "frontEnd/prototypes/glassWorld/dist/antennaWidget.html"
        bundle.parent.mkdir(parents=True)
        bundle.write_text("<!doctype html><p>candidate</p>")
        self.assertIn("candidate", fn())
        bundle.write_bytes(b"x" * (app.MAX_WIDGET_BYTES + 1))
        with self.assertRaises(ValueError):
            fn()

    @unittest.skipUnless(importlib.util.find_spec("mcp"), "Pinned MCP package not installed")
    def test_real_mcp_structured_results(self):
        from mcp.server import MCPServer
        from mcp.types import ToolAnnotations

        async def verify():
            server = MCPServer("antenna-integration-test")
            app.register_antenna(server, root=self.root, annotations=ToolAnnotations(readOnlyHint=True))
            for name, arguments in (("luhm_open_antenna", {}), ("luhm_plan_antenna_creation", {
                "recipe": "characterAnimation", "target": "remoteStudio", "brief": "Original dance"})):
                result = await server.call_tool(name, arguments)
                self.assertIsNotNone(result.structured_content)
                self.assertFalse(result.structured_content["executionEnabled"])
            self.assertEqual(len(await server.read_resource(app.URI)), 1)

        asyncio.run(verify())


if __name__ == "__main__":
    unittest.main()
