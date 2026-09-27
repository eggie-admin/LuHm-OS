#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTOR = ROOT / "tools/doctorOniAudit.py"
ROUTER = ROOT / "tools/lumTaskRouter.py"
SHA = "a" * 40


class AgentMeshV2Tests(unittest.TestCase):
    def make_bundle(self, root: Path, name: str, *, source_sha: str = SHA, version: str = "1.0.25") -> None:
        root.mkdir(parents=True, exist_ok=True)
        (root / "cathedral-atelier-receipt.txt").write_text(
            f"source_sha={source_sha}\n"
            "status=CATHEDRAL_ONI_ATELIER_CI_PROOF\n"
            "package=art.eggiebagelface.luhmos.cathedraltoy.atelier\n"
            f"version={version}\n",
            encoding="utf-8",
        )
        for file_name in ("badging.txt", "manifest.txt", "signature.txt", "zipalign.txt", "sha256.txt"):
            (root / file_name).write_text("verified\n", encoding="utf-8")
        (root / "source-components-sha256.txt").write_text(
            "1" * 64 + "  addons/kai_webview/bin/kaiwebview-debug.aar\n" +
            "2" * 64 + "  cockpit/package-lock.json\n",
            encoding="utf-8",
        )
        role = "builder_a" if name == "Tetsu" else "builder_b"
        (root / "oni-builder.json").write_text(json.dumps({
            "schema": "luhm-os.oni-builder-receipt.v1",
            "name": name,
            "role": role,
            "sourceSha": source_sha,
            "runId": "42",
            "jobId": f"build-{name.lower()}",
            "workflow": "test",
            "timestampUtc": "2026-09-27T00:00:00+00:00",
            "promotionAuthority": False,
        }), encoding="utf-8")

    def run_doctor(self, tetsu: Path, kaji: Path, out: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([
            "python3", str(DOCTOR),
            "--expected-sha", SHA,
            "--tetsu", str(tetsu),
            "--kaji", str(kaji),
            "--output", str(out),
        ], text=True, capture_output=True)

    def run_route(self, *args: str) -> dict:
        result = subprocess.run(["python3", str(ROUTER), *args], text=True, capture_output=True, check=True)
        return json.loads(result.stdout)

    def test_dual_build_green(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self.make_bundle(base / "Tetsu", "Tetsu")
            self.make_bundle(base / "Kaji", "Kaji")
            out = base / "verdict.json"
            result = self.run_doctor(base / "Tetsu", base / "Kaji", out)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads(out.read_text())
            self.assertEqual(report["status"], "GREEN_DOCTOR_ONI_DUAL_BUILD_PROVEN")

    def test_missing_evidence_is_unknown_not_green(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self.make_bundle(base / "Tetsu", "Tetsu")
            self.make_bundle(base / "Kaji", "Kaji")
            (base / "Kaji" / "signature.txt").unlink()
            out = base / "verdict.json"
            result = self.run_doctor(base / "Tetsu", base / "Kaji", out)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads(out.read_text())
            self.assertTrue(report["status"].startswith("UNKNOWN_"))

    def test_semantic_disagreement_is_amber(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self.make_bundle(base / "Tetsu", "Tetsu")
            self.make_bundle(base / "Kaji", "Kaji", version="9.9.9")
            out = base / "verdict.json"
            result = self.run_doctor(base / "Tetsu", base / "Kaji", out)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads(out.read_text())
            self.assertEqual(report["status"], "AMBER_DOCTOR_ONI_BUILD_DIVERGENCE")
            self.assertIn("receipt.version", report["divergences"])

    def test_stale_sha_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            self.make_bundle(base / "Tetsu", "Tetsu", source_sha="b" * 40)
            self.make_bundle(base / "Kaji", "Kaji")
            out = base / "verdict.json"
            result = self.run_doctor(base / "Tetsu", base / "Kaji", out)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads(out.read_text())
            self.assertTrue(report["status"].startswith("RED_"))

    def test_build_route_uses_two_builders_and_doctor(self) -> None:
        report = self.run_route("build")
        self.assertEqual(report["parallelBuilds"], 2)
        self.assertEqual(report["sourceMutationLanes"], 1)
        self.assertIn("Tetsu", report["workers"])
        self.assertIn("Kaji", report["workers"])
        self.assertIn("DrNao", report["workers"])
        self.assertFalse(report["greenAuthority"])

    def test_direct_route_bypasses_mesh(self) -> None:
        report = self.run_route("direct")
        self.assertEqual(report["workers"], ["Lum"])
        self.assertEqual(report["parallelBuilds"], 0)

    def test_art_route_is_small_and_does_not_build(self) -> None:
        report = self.run_route("art")
        self.assertEqual(report["workers"], ["Lum", "Yume"])
        self.assertEqual(report["parallelBuilds"], 0)
        self.assertEqual(report["sourceMutationLanes"], 0)

    def test_media_route_adds_asset_curator(self) -> None:
        report = self.run_route("media")
        self.assertEqual(report["workers"], ["Lum", "Yume", "Sumi"])
        self.assertEqual(report["supportWorkers"], ["Yume", "Sumi"])

    def test_dictation_never_executes_directly(self) -> None:
        report = self.run_route("dictation")
        self.assertEqual(report["workers"], ["Lum", "Koe"])
        self.assertEqual(report["sourceMutationLanes"], 0)
        self.assertFalse(report["dictationExecutesDirectly"])

    def test_creative_truth_claim_can_add_doctor_without_builders(self) -> None:
        report = self.run_route("art", "--truth-sensitive", "--asset-review")
        self.assertIn("Yume", report["workers"])
        self.assertIn("Sumi", report["workers"])
        self.assertIn("DrNao", report["workers"])
        self.assertEqual(report["parallelBuilds"], 0)
        self.assertTrue(report["requiresDoctorVerdict"])


if __name__ == "__main__":
    unittest.main()
