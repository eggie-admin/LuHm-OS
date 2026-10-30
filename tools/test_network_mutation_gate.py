#!/usr/bin/env python3
"""Offline network/AI mutation gate tests. No subprocesses, sockets or host changes."""
import unittest

ALLOWED = frozenset({"inventory.read", "health.read", "config.diff.read"})
NETWORK_MUTATIONS = frozenset({"netplan.apply", "vpn.restart", "tls.rotate",
                               "firewall.write", "loadbalancer.deploy",
                               "firmware.flash", "kernel.upgrade"})
TARGETS = frozenset({"local", "raspberry-pi", "remote-vm", "samsung"})


def classify(request):
    if not isinstance(request, dict) or set(request) != {"target", "action", "sourceSha", "approval"}:
        raise ValueError("invalid request shape")
    if request["target"] not in TARGETS:
        raise ValueError("unknown target")
    sha = request["sourceSha"]
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("invalid source SHA")
    if request["approval"] is not False:
        raise PermissionError("no approval may be delegated through request data")
    action = request["action"]
    if action in ALLOWED:
        return {"status": "READ_ONLY_PROPOSAL", "executionAllowed": False}
    if action in NETWORK_MUTATIONS:
        raise PermissionError("mutation requires separate out-of-band authorization")
    raise PermissionError("unknown action denied")


class NetworkMutationGate(unittest.TestCase):
    def setUp(self):
        self.request = {"target": "remote-vm", "action": "health.read",
                        "sourceSha": "a" * 40, "approval": False}

    def test_read_only(self):
        self.assertFalse(classify(self.request)["executionAllowed"])

    def test_mutations_denied(self):
        for action in NETWORK_MUTATIONS:
            with self.subTest(action=action), self.assertRaises(PermissionError):
                classify({**self.request, "action": action})

    def test_unrecognized_denied(self):
        with self.assertRaises(PermissionError):
            classify({**self.request, "action": "shell.exec"})

    def test_self_approval_denied(self):
        with self.assertRaises(PermissionError):
            classify({**self.request, "approval": True})

    def test_unknown_target_denied(self):
        with self.assertRaises(ValueError):
            classify({**self.request, "target": "production-everywhere"})

    def test_unknown_fields_denied(self):
        with self.assertRaises(ValueError):
            classify({**self.request, "command": "netplan apply"})

    def test_invalid_sha_denied(self):
        with self.assertRaises(ValueError):
            classify({**self.request, "sourceSha": "latest"})


if __name__ == "__main__":
    unittest.main()
