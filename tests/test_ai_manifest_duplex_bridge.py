"""Offline only: packet integrity, two distinct product tracks and explicit deny cases."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "aiManifestDuplexBridge", ROOT / "host/api/ai-manifest-duplex-bridge.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
SOURCE = "a" * 40


def task(track):
    return mod.candidate_manifest(task_id="cast-" + track, scope_id=track + "-track",
                                  source_ref=SOURCE)


class AiManifestDuplexBridgeTests(unittest.TestCase):
    def test_both_tracks_manifest_base64_and_real_binary(self):
        for track in ("app", "plugin"):
            with self.subTest(track=track):
                packet = task(track)
                projection = mod.feed_projection(packet)
                self.assertFalse(projection["executable"])
                self.assertEqual(mod.decode_projection(projection), packet)
                wire = mod.offline_frame(packet, track=track, correlation_id=900)
                self.assertEqual(mod.decode_offline_frame(
                    wire, expected_track=track, expected_sha=SOURCE), packet)
                self.assertEqual(mod.decode_frame(wire).lane, 3)
                self.assertEqual(mod.decode_frame(wire).stream_id, mod.STREAM_IDS[track])

    def test_live_in_memory_duplex_with_two_tracks_and_durable_acks(self):
        # This is an offline proof of traffic BOTH directions, not provider I/O.
        from duplexTypedBusCodec import DuplexPeer
        app_peer = DuplexPeer(max_in_flight=1)
        plugin_peer = DuplexPeer(max_in_flight=1)
        app_packet = task("app")
        plugin_packet = task("plugin")
        app_wire = app_peer.send(
            stream_id=mod.STREAM_IDS["app"], lane=3,
            payload=mod.validate_manifest(app_packet), correlation_id=416)
        plugin_wire = plugin_peer.send(
            stream_id=mod.STREAM_IDS["plugin"], lane=3,
            payload=mod.validate_manifest(plugin_packet), correlation_id=427)
        self.assertEqual(app_peer.receive(plugin_wire)[0], "needsDurableCommit")
        self.assertEqual(plugin_peer.receive(app_wire)[0], "needsDurableCommit")
        self.assertEqual(len(app_peer.pending), 1)
        self.assertEqual(len(plugin_peer.pending), 1)
        status_app, app_ack, app_received = plugin_peer.receive(app_wire, durable_commit=True)
        status_plugin, plugin_ack, plugin_received = app_peer.receive(
            plugin_wire, durable_commit=True)
        self.assertEqual((status_app, status_plugin), ("accepted", "accepted"))
        self.assertEqual((app_received.correlation_id, plugin_received.correlation_id),
                         (416, 427))
        self.assertEqual(mod.decode_offline_frame(
            app_wire, expected_track="app", expected_sha=SOURCE), app_packet)
        self.assertEqual(mod.decode_offline_frame(
            plugin_wire, expected_track="plugin", expected_sha=SOURCE), plugin_packet)
        app_peer.receive(app_ack)
        plugin_peer.receive(plugin_ack)
        self.assertFalse(app_peer.pending)
        self.assertFalse(plugin_peer.pending)
        self.assertEqual((app_peer.received[12], plugin_peer.received[11]), (1, 1))

    def test_cross_track_and_source_replay_rejected(self):
        wire = mod.offline_frame(task("app"), track="app", correlation_id=1)
        with self.assertRaisesRegex(ValueError, "RED_WRONG_MANIFEST_STREAM"):
            mod.decode_offline_frame(wire, expected_track="plugin", expected_sha=SOURCE)
        with self.assertRaisesRegex(ValueError, "RED_FRAME_SOURCE_OR_PAYLOAD"):
            mod.decode_offline_frame(wire, expected_track="app", expected_sha="b"*40)
        with self.assertRaisesRegex(ValueError, "RED_UNKNOWN_TRACK"):
            mod.offline_frame(task("app"), track="public", correlation_id=1)

    def test_no_ambient_execution_or_secret_route(self):
        packet = task("plugin")
        packet["authority"]["mutation"] = True
        with self.assertRaisesRegex(ValueError, "RED_AUTHORITY"):
            mod.validate_manifest(packet)
        packet = task("plugin")
        packet["apiKey"] = "pretend"
        with self.assertRaisesRegex(ValueError, "RED_MANIFEST_FIELDS"):
            mod.validate_manifest(packet)
        packet = task("app")
        packet["inputRefs"] = ["https://example.com/token=hidden"]
        with self.assertRaisesRegex(ValueError, "RED_INPUT_REFS"):
            mod.validate_manifest(packet)
        packet = task("app")
        packet["budget"]["maxRequests"] = 999
        with self.assertRaisesRegex(ValueError, "RED_BUDGET"):
            mod.validate_manifest(packet)

    def test_feed_rejects_base64_tamper_even_with_valid_json(self):
        packet = task("app")
        projection = mod.feed_projection(packet)
        projection["taskId"] = "swapped"
        with self.assertRaisesRegex(ValueError, "RED_FEED_TAMPER_OR_NONCANONICAL"):
            mod.decode_projection(projection)
        projection = mod.feed_projection(packet)
        projection["payloadBase64"] += "!"
        with self.assertRaisesRegex(ValueError, "RED_FEED_DECODE"):
            mod.decode_projection(projection)
        projection = mod.feed_projection(packet)
        projection["executable"] = True
        with self.assertRaisesRegex(ValueError, "RED_FEED_AUTHORITY"):
            mod.decode_projection(projection)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "RED_DUPLICATE_JSON_KEY"):
            json.loads('{"a":1,"a":2}', object_pairs_hook=mod.no_duplicates)

    def test_existing_bus_is_reference_only_and_no_api_credentials(self):
        bridge=(ROOT / "host/api/ai-manifest-duplex-bridge.py").read_text()
        contract=(ROOT / "doctrine/duplexTypedBusV1.yaml").read_text()
        self.assertIn("noRemotePacketsSent: true", contract)
        self.assertIn("noSqlMigrationApplied: true", contract)
        self.assertIn("STREAM_IDS = {\"app\": 11, \"plugin\": 12}", bridge)
        self.assertNotIn("requests.post(", bridge)
        self.assertNotIn("urlopen(", bridge)
        self.assertNotIn("openai.api_key", bridge)
        self.assertNotIn("google.generativeai", bridge)


if __name__ == "__main__":
    unittest.main()
