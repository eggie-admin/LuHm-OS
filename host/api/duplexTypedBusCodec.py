"""LuHm internal Protobuf-wire subset reference, no socket or SQL writes.

Frame fields 1..8 match duplexTypedBusV1.proto. For v1 this proof handles
bounded numeric signed-int payloads and opaque validated typed lane packets.
Do not use as a production router without a vetted Protobuf runtime and
authenticated durable adapters. Hex output is diagnostic only.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict

MAX_PAYLOAD = 4096
MAX_FRAME = 8192
MAX_U64 = (1 << 64) - 1
KINDS = frozenset((1, 2, 3, 4, 5, 6))
LANES = frozenset((0, 1, 2, 3))


class WireError(ValueError):
    pass


def varint(value: int) -> bytes:
    if type(value) is not int or not 0 <= value <= MAX_U64:
        raise WireError("RED_UINT64")
    out = bytearray()
    while value >= 128:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return bytes(out)


def read_varint(data: bytes, offset: int) -> tuple[int, int]:
    start = offset
    v = 0
    for i in range(10):
        if offset >= len(data):
            raise WireError("RED_TRUNCATED_VARINT")
        octet = data[offset]
        offset += 1
        if i == 9 and octet > 1:
            raise WireError("RED_VARINT_OVERFLOW")
        v |= (octet & 127) << (7 * i)
        if not octet & 128:
            if data[start:offset] != varint(v):
                raise WireError("RED_NONCANONICAL_VARINT")
            return v, offset
    raise WireError("RED_VARINT_TOO_LONG")


def int_payload(value: int) -> bytes:
    if type(value) is not int or not -(1 << 63) <= value < (1 << 63):
        raise WireError("RED_SIGNED_INT64")
    zigzag = (value << 1) ^ (value >> 63)
    # NumericPayload.signed_integer = 1, wire type VARINT (0)
    return b"\x08" + varint(zigzag)


def parse_int_payload(blob: bytes) -> int:
    if not blob.startswith(b"\x08"):
        raise WireError("RED_NUMERIC_FIELD")
    value, end = read_varint(blob, 1)
    if end != len(blob):
        raise WireError("RED_NUMERIC_TRAILING")
    return (value >> 1) ^ -(value & 1)


@dataclass(frozen=True)
class Frame:
    version: int = 1
    lane: int = 0
    kind: int = 1
    stream_id: int = 1
    sequence_id: int = 1
    ack_sequence: int = 0
    correlation_id: int = 0
    payload: bytes = b""

    def validate(self):
        if self.version != 1 or self.kind not in KINDS or self.lane not in LANES:
            raise WireError("RED_VERSION_KIND_LANE")
        for field in ("stream_id", "sequence_id", "ack_sequence", "correlation_id"):
            v = getattr(self, field)
            if type(v) is not int or not 0 <= v <= MAX_U64:
                raise WireError("RED_FIELD_RANGE")
        if not 1 <= self.stream_id <= 65535:
            raise WireError("RED_STREAM_ID")
        if not isinstance(self.payload, bytes) or len(self.payload) > MAX_PAYLOAD:
            raise WireError("RED_PAYLOAD_SIZE")
        if self.kind in (1, 3):
            if self.sequence_id == 0 or len(self.payload) == 0:
                raise WireError("RED_DATA_FRAME")
        elif self.payload:
            raise WireError("RED_CONTROL_PAYLOAD")
        if self.kind == 2 and self.sequence_id != 0:
            raise WireError("RED_ACK_SEQUENCE_FIELD")
        return self


def encode_frame(frame: Frame) -> bytes:
    frame.validate()
    out = bytearray()
    values = (frame.version, frame.lane, frame.kind, frame.stream_id,
              frame.sequence_id, frame.ack_sequence, frame.correlation_id)
    for i, value in enumerate(values, 1):
        if value:
            out += varint((i << 3) | 0)
            out += varint(value)
    if frame.payload:
        out += b"\x42" + varint(len(frame.payload)) + frame.payload
    if len(out) > MAX_FRAME:
        raise WireError("RED_FRAME_OVERSIZE")
    return bytes(out)


def decode_frame(data: bytes) -> Frame:
    if not isinstance(data, bytes) or not data or len(data) > MAX_FRAME:
        raise WireError("RED_FRAME_SIZE")
    values = {}
    i = 0
    while i < len(data):
        tag, i = read_varint(data, i)
        field, wire_type = tag >> 3, tag & 7
        if field not in range(1, 9) or field in values:
            raise WireError("RED_UNKNOWN_OR_DUPLICATE_FIELD")
        if field == 8:
            if wire_type != 2:
                raise WireError("RED_WRONG_PAYLOAD_WIRE")
            length, i = read_varint(data, i)
            if length > MAX_PAYLOAD or length > len(data) - i:
                raise WireError("RED_BAD_PAYLOAD_LENGTH")
            values[field] = data[i:i + length]
            i += length
        else:
            if wire_type != 0:
                raise WireError("RED_WRONG_FIELD_WIRE")
            values[field], i = read_varint(data, i)
    frame = Frame(
        version=values.get(1, 0), lane=values.get(2, 0),
        kind=values.get(3, 0), stream_id=values.get(4, 0),
        sequence_id=values.get(5, 0), ack_sequence=values.get(6, 0),
        correlation_id=values.get(7, 0), payload=values.get(8, b""),
    )
    frame.validate()
    # Reject noncanonical order and explicit zeros in the reference v1 subset.
    if encode_frame(frame) != data:
        raise WireError("RED_NONCANONICAL_FRAME")
    return frame


class DuplexPeer:
    """Offline model; a production adapter MUST persist inbound before ack."""
    def __init__(self, max_in_flight: int = 32):
        if not 1 <= max_in_flight <= 32:
            raise WireError("RED_WINDOW")
        self.max_in_flight = max_in_flight
        self.sent = defaultdict(int)
        self.received = defaultdict(int)
        self.pending = {}

    def send(self, *, stream_id: int, lane: int, payload: bytes,
             correlation_id: int, kind: int = 1) -> bytes:
        if kind not in (1, 3):
            raise WireError("RED_SEND_KIND")
        if sum(k[0] == stream_id for k in self.pending) >= self.max_in_flight:
            raise WireError("RED_BACKPRESSURE_WINDOW")
        next_seq = self.sent[stream_id] + 1
        frame = Frame(lane=lane, kind=kind, stream_id=stream_id,
                      sequence_id=next_seq, ack_sequence=self.received[stream_id],
                      correlation_id=correlation_id, payload=payload)
        blob = encode_frame(frame)
        self.sent[stream_id] = next_seq
        self.pending[(stream_id, next_seq)] = blob
        return blob

    def receive(self, blob: bytes, *, durable_commit: bool = False) -> tuple[str, bytes | None, Frame]:
        frame = decode_frame(blob)
        stream_id = frame.stream_id
        if frame.ack_sequence > self.sent[stream_id]:
            raise WireError("RED_ACK_AHEAD_OF_SENT")
        for key in list(self.pending):
            if key[0] == stream_id and key[1] <= frame.ack_sequence:
                del self.pending[key]
        if frame.kind == 2:
            return "ack", None, frame
        if frame.kind not in (1, 3):
            return "control", None, frame
        expected = self.received[stream_id] + 1
        if frame.sequence_id > expected:
            raise WireError("RED_SEQUENCE_GAP")
        if frame.sequence_id == expected and not durable_commit:
            return "needsDurableCommit", None, frame
        if frame.sequence_id == expected:
            self.received[stream_id] = frame.sequence_id
            status = "accepted"
        else:
            status = "duplicate"
        ack = Frame(kind=2, lane=frame.lane, stream_id=stream_id,
                    sequence_id=0, ack_sequence=self.received[stream_id],
                    correlation_id=frame.correlation_id)
        return status, encode_frame(ack), frame
