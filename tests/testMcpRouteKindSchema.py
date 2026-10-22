import asyncio
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "host" / "mcp"))
import luhmMcpServer as core


class RouteKindSchemaContract(unittest.TestCase):
    def testToolPublishesCanonicalRouteEnum(self):
        async def inspect():
            tools = await core.server.list_tools()
            route = next(tool for tool in tools if tool.name == "luhm_route_task")
            wire = route.model_dump(by_alias=True)
            kind_schema = wire["inputSchema"]["properties"]["kind"]
            self.assertEqual(set(kind_schema["enum"]), core.ROUTE_KINDS)
            self.assertEqual(core.ROUTE_KINDS, set(core.get_args(core.RouteKind)))
            self.assertTrue(route.annotations.read_only_hint)
            self.assertFalse(route.annotations.destructive_hint)

            alignment = json.loads(
                (Path(__file__).resolve().parents[1] / "doctrine" / "driveControlPlaneAlignmentV1.json").read_text()
            )
            self.assertFalse(alignment["githubSource"]["driveFolderIdsOrUrlsStoredInPublicRepository"])
            serialized = json.dumps(alignment)
            self.assertNotIn("drive.google.com", serialized)
            for row in alignment["driveTree"]:
                self.assertFalse(any("id" in key.lower() or "url" in key.lower() for key in row))
        asyncio.run(inspect())


if __name__ == "__main__":
    unittest.main()
