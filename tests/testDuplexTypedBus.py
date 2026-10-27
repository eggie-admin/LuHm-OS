"""Wire-bytes and symmetric packet exchange with no network or database side effects."""
import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "host/api/duplexTypedBusCodec.py"
SPEC = importlib.util.spec_from_file_location("luhmDuplexCodec", TARGET)
import sys
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

class DuplexBusTests(unittest.TestCase):
    def test_numeric_proto_wire_and_hex_only_for_logs(self):
        for x in (-1000, -1, 0, 1, 150, 2**31):
            payload = mod.int_payload(x)
            self.assertEqual(mod.parse_int_payload(payload), x)
            packet = mod.Frame(stream_id=1, lane=0, kind=1, sequence_id=1,
                               correlation_id=42, payload=payload)
            raw = mod.encode_frame(packet)
            self.assertEqual(mod.decode_frame(raw),packet)
            self.assertLess(len(raw),len(raw.hex()))

    def test_symmetric_round_trip_with_ack_correlation(self):
        local = mod.DuplexPeer()
        remote = mod.DuplexPeer()
        request=local.send(stream_id=7,lane=0,payload=mod.int_payload(150),correlation_id=991)
        before, not_yet, frame=remote.receive(request)
        self.assertEqual((before,not_yet),("needsDurableCommit",None))
        self.assertEqual(remote.received[7],0)
        accepted, ack, request_frame=remote.receive(request,durable_commit=True)
        self.assertEqual(accepted,"accepted")
        self.assertEqual(mod.parse_int_payload(request_frame.payload),150)
        local.receive(ack)
        self.assertFalse(local.pending)
        response=remote.send(stream_id=7,lane=0,payload=mod.int_payload(151),kind=3,correlation_id=991)
        received, ack2, result=local.receive(response,durable_commit=True)
        self.assertEqual(received,"accepted")
        self.assertEqual(result.kind,3)
        self.assertEqual(result.correlation_id,request_frame.correlation_id)
        self.assertEqual(mod.parse_int_payload(result.payload),151)
        remote.receive(ack2)
        self.assertFalse(remote.pending)

    def test_true_full_duplex_multiple_streams(self):
        left=mod.DuplexPeer()
        right=mod.DuplexPeer()
        l=left.send(stream_id=1,lane=0,payload=mod.int_payload(7),correlation_id=9)
        r=right.send(stream_id=2,lane=0,payload=mod.int_payload(8),correlation_id=10)
        self.assertEqual(left.receive(r,durable_commit=True)[0],"accepted")
        self.assertEqual(right.receive(l,durable_commit=True)[0],"accepted")
        self.assertEqual(left.received[2],1)
        self.assertEqual(right.received[1],1)
        self.assertEqual(left.received[1],0)

    def test_duplicate_is_idempotently_acked(self):
        one=mod.DuplexPeer()
        two=mod.DuplexPeer()
        packet=one.send(stream_id=1,lane=0,payload=mod.int_payload(9),correlation_id=33)
        self.assertEqual(two.receive(packet,durable_commit=True)[0],"accepted")
        self.assertEqual(two.receive(packet,durable_commit=True)[0],"duplicate")
        self.assertEqual(two.received[1],1)

    def test_ack_ahead_rejected(self):
        p=mod.DuplexPeer()
        bad=mod.encode_frame(mod.Frame(kind=2,stream_id=1,sequence_id=0,ack_sequence=12))
        with self.assertRaisesRegex(mod.WireError,"RED_ACK_AHEAD_OF_SENT"):
            p.receive(bad)

    def test_backpressure_bounded(self):
        p=mod.DuplexPeer(max_in_flight=1)
        p.send(stream_id=1,lane=0,payload=mod.int_payload(1),correlation_id=1)
        with self.assertRaisesRegex(mod.WireError,"RED_BACKPRESSURE_WINDOW"):
            p.send(stream_id=1,lane=0,payload=mod.int_payload(2),correlation_id=2)
        p.send(stream_id=2,lane=0,payload=mod.int_payload(3),correlation_id=3)

    def test_packet_sequence_gap_rejected(self):
        p=mod.DuplexPeer()
        pkt=mod.encode_frame(mod.Frame(sequence_id=2,payload=mod.int_payload(2)))
        with self.assertRaisesRegex(mod.WireError,"RED_SEQUENCE_GAP"):
            p.receive(pkt,durable_commit=True)

    def test_rejected_sequence_cannot_consume_outstanding_ack(self):
        sender = mod.DuplexPeer()
        original = sender.send(stream_id=4, lane=0,
                               payload=mod.int_payload(17), correlation_id=17)
        self.assertTrue(original)
        pending_before = dict(sender.pending)
        # Malicious/out-of-order inbound packet claims ACK=1 for the original.
        # The invalid sequence must not silently release the sender window.
        future = mod.encode_frame(mod.Frame(
            stream_id=4, lane=0, kind=1, sequence_id=2, ack_sequence=1,
            correlation_id=18, payload=mod.int_payload(18)))
        with self.assertRaisesRegex(mod.WireError, "RED_SEQUENCE_GAP"):
            sender.receive(future, durable_commit=True)
        self.assertEqual(sender.pending, pending_before)
        self.assertEqual(sender.received[4], 0)

    def test_corruption_and_unrecognized_version_rejected(self):
        x=mod.encode_frame(mod.Frame(payload=mod.int_payload(5)))
        for broken in (x + b"\xff",b"",b"\x08\x02"+x[2:],x + b"\x08\x01",x + b"\x40\x01"):
            with self.assertRaises(mod.WireError):
                mod.decode_frame(broken)

    def test_limited_payload_and_signed_type(self):
        with self.assertRaisesRegex(mod.WireError,"RED_SIGNED_INT64"):
            mod.int_payload(2**63)
        with self.assertRaisesRegex(mod.WireError,"RED_PAYLOAD_SIZE"):
            mod.encode_frame(mod.Frame(payload=b"x"*4097))
        with self.assertRaisesRegex(mod.WireError,"RED_NUMERIC_FIELD"):
            mod.parse_int_payload(b"\x01\x01")

    def test_schema_and_zero_live_mutations(self):
        proto=(ROOT/"host/api/duplexTypedBusV1.proto").read_text()
        sql=(ROOT/"host/api/duplexTypedBusV1.sql").read_text()
        yaml=(ROOT/"doctrine/duplexTypedBusV1.yaml").read_text()
        for field in ("uint32 version = 1;", "Lane lane = 2;", "Kind kind = 3;",
                      "uint32 stream_id = 4;", "uint64 sequence_id = 5;",
                      "uint64 ack_sequence = 6;", "uint64 correlation_id = 7;",
                      "bytes payload = 8;"):
            self.assertIn(field,proto)
        for t in ("luhm_duplex_outbox","luhm_duplex_inbox","luhm_duplex_cursor"):
            self.assertIn(t,sql)
        self.assertNotIn("DROP TABLE",sql)
        self.assertNotIn("TRIGGER",sql.upper())
        self.assertIn("sqlCanExecuteJavaScript: false",yaml)
        self.assertIn("binaryTransport: true",yaml)
        self.assertIn("applicationMcp: existingJsonRpcStreamableHttpUnchanged",yaml)
        self.assertIn("newPublicEndpoint: false",yaml)
        self.assertIn("noRemotePacketsSent: true",yaml)

if __name__=="__main__":
    unittest.main()
