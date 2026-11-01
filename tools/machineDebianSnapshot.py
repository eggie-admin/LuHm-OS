#!/usr/bin/env python3
"""LuHm OS: reproducible source or redacted read-only Linux machine snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sqlite3
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/machineDebianFourLayerV1.json"
LAYERS = ("kernel", "system", "studio", "interface")
PHASES = ("inventory", "bound", "verify", "propose")
PROFILES = ("headless", "kiosk", "studio", "rescue")
EMULATORS = ("dolphin", "pcsx2", "duckstation", "libretro", "scummvm")
TOOLS = ("python3", "git", "ffmpeg", "ffprobe", "godot", "blender", "chromium", "firefox")
EXPECTED_REFS = (
    "doctrine/machineToHumanWizardV1.json",
    "doctrine/typedFourLaneSqlV1.json",
    "doctrine/vendorReductionV1.json",
    "doctrine/artistFirstArtToolCanonV1.json",
    ".devcontainer/Dockerfile",
    "host/ai-ffmpeg/ai-ffmpeg.py",
    "tools/machineToHumanWizard.py",
)
OFFICIAL_HOSTS = {
    "www.debian.org", "d-i.debian.org", "www.kernel.org", "docs.kernel.org",
    "www.ffmpeg.org", "docs.libretro.com",
}
STUDY_HOSTS = {"github.com", "docs.libretro.com", "www.scummvm.org"}
SAFE_FACTS = {"system", "arch", "kernelRelease", "distroId", "distroVersion",
              "logicalCpuCount", "pageBytes", "memTotalBytes", "memAvailableBytes"}
SAFE_TEXT = re.compile(r"[a-zA-Z0-9_.+~-]{1,80}\Z")
EXPECTED_GUARDS = (
    "noHostPackageChanges", "noKernelCompile", "noKernelInstall", "noModprobe",
    "noBiosWrite", "noSecureBootChange", "noGrubWrite", "noPartitionWrite",
    "noGpartedExecution", "noNetworkListener", "noPublicSQL", "noEmulatorLaunch",
    "noBiosRomDownload", "noGameAssetExtraction", "noNvidiaInstall",
    "noAgentRelease", "noMainMerge", "noPublicDeployment", "noPaidCloudProvision",
)


class MachineAuditError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise MachineAuditError(reason)


def safe_source(root: Path, name: object) -> Path:
    require(type(name) is str and len(name) <= 140 and bool(name), "SOURCE_NAME")
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in name,
            "SOURCE_PATH_ESCAPE")
    actual = root / path
    require(actual.is_file() and not actual.is_symlink() and
            actual.resolve().is_relative_to(root.resolve()), "SOURCE_MISSING_OR_LINK")
    return actual


def source_receipts(root: Path, paths: tuple[str, ...]) -> list[dict]:
    out = []
    for name in paths:
        path = safe_source(root, name)
        # No unbounded parsing, no symlinks and no binary user media in receipts.
        with path.open("rb") as file:
            data = file.read(1_048_577)
        require(0 < len(data) <= 1_048_576, "SOURCE_SIZE_LIMIT")
        out.append({"source": name, "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest()})
    return out


def valid_url(url: object, hosts: set[str]) -> bool:
    if type(url) is not str or len(url) > 260:
        return False
    parts = urlsplit(url)
    return (parts.scheme == "https" and parts.hostname in hosts
            and parts.username is None and parts.password is None
            and parts.fragment == "")


def check_contract(m: object, root: Path = ROOT) -> list[dict]:
    require(type(m) is dict and m.get("schema") == "luhmOs.machineDebianFourLayer.v1",
            "MACHINE_CONTRACT_SCHEMA")
    require(m.get("authority") == "Professor" and m.get("status") == "PROPOSED_SOURCE_ONLY"
            and m.get("crownStatus") == "STOP", "MACHINE_AUTHORITY")
    require(m.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.",
            "MACHINE_SOURCE_LAW")
    t = m.get("target", {})
    require(t.get("hostDistro") == "Debian" and t.get("hostRelease") == "13" and
            t.get("codename") == "trixie" and t.get("physicalBackendCountTarget") == 1,
            "MACHINE_ONE_HOST_TARGET")
    require(t.get("kernelFork") == "NOT_AUTHORIZED" and
            t.get("sameBinaryAcrossAbis") is False and
            t.get("x86_64") is True and t.get("aarch64") is True and
            all(t.get(k) is False for k in ("actualHostVerified", "actualKconfigVerified",
                 "driverBindingVerified", "firmwareVersionVerified", "bootSignatureVerified")),
            "MACHINE_KERNEL_TRUTH")
    layers = m.get("layers", [])
    require(type(layers) is list and [r.get("id") for r in layers] == list(LAYERS) and
            [r.get("hex") for r in layers] == ["0x00", "0x04", "0x08", "0x0C"] and
            m.get("phases") == list(PHASES), "MACHINE_LAYER_AXES")
    cells = m.get("matrix", [])
    require(type(cells) is list and len(cells) == 16, "MACHINE_4X4")
    for i, cell in enumerate(cells):
        require(type(cell) is dict and cell == {
            "index": i, "hex": f"0x{i:02X}", "layer": LAYERS[i // 4],
            "phase": PHASES[i % 4], "status": "SOURCE_CONTRACT_ONLY",
            "physicalProof": False}, "MACHINE_LOGICAL_HEX")
    profiles = m.get("profiles", [])
    require(type(profiles) is list and [p.get("id") for p in profiles] == list(PROFILES)
            and [p.get("order") for p in profiles] == list(range(4))
            and [p.get("alwaysRequired") for p in profiles] == [True, False, False, False],
            "MACHINE_PROFILE_LADDER")
    require(profiles[0].get("desktop") == "NONE" and
            all(p.get("service") and isinstance(p.get("packages"), list)
                and isinstance(p.get("optional"), list) for p in profiles),
            "MACHINE_HEADLESS_MINIMUM")
    require(profiles[0]["packages"] == ["python3", "ca-certificates", "git"],
            "MACHINE_HEADLESS_VENDOR_FAT")
    desktops = m.get("optionalDesktops", [])
    require([d.get("id") for d in desktops] ==
            ["none", "gnome", "cinnamon", "browserKiosk"] and
            [d.get("default") for d in desktops] == [True, False, False, False],
            "MACHINE_DESKTOP_MINIMUM")
    b = m.get("boundaries", {})
    for k in ("grub", "gparted", "android", "ios", "nvidia", "ffmpeg",
              "sql", "ai", "git", "googleDrive", "webKiosk"):
        require(type(b.get(k)) is str and bool(b[k]), "MACHINE_BOUNDARY_MISSING")
    require(all(m.get("safety", {}).get(g) is True for g in EXPECTED_GUARDS) and
            set(m.get("safety", {})) == set(EXPECTED_GUARDS), "MACHINE_PRIVILEGE_BARRIER")
    emus = m.get("studyOnly", [])
    require([e.get("id") for e in emus] == list(EMULATORS) and
            all(e.get("decision") == "STUDY_ONLY" and
                e.get("copyToLuHmCore") is False and
                valid_url(e.get("source"), STUDY_HOSTS) for e in emus),
            "MACHINE_EMULATOR_POLICY")
    require([e.get("license") for e in emus][:2] ==
            ["GPL-2.0-or-later", "GPL-3.0"], "MACHINE_LICENSE_POLICY")
    require(m.get("requestedReads") == list(EXPECTED_REFS), "MACHINE_CANON_REFS")
    require(len(m.get("officialRefs", [])) >= 6 and
            all(valid_url(url, OFFICIAL_HOSTS) for url in m["officialRefs"]),
            "MACHINE_UPSTREAM_REFS")
    sp = m.get("snapshot", {})
    require(sp.get("supportedModes") == ["source", "fixture", "host-read-only"] and
            all(sp.get(k) is True for k in (
                "privateIdentifiersExcluded", "skipKernelCmdline", "realDeviceProofRequired",
                "unverifiedDoesNotBecomeGreen", "sqliteInMemoryOnly")) and
            sp.get("sourceHashAlgorithm") == "sha256" and
            sp.get("numericMeasurements") ==
            ["logicalCpuCount", "pageBytes", "memTotalBytes", "memAvailableBytes"],
            "MACHINE_SNAPSHOT_MODE")
    require(m.get("nextGates") == [
        "exactSourceSmoke", "actualDebianHostInventory",
        "kernelConfigAndSecureBootAuthorityReadback", "abiAndDriverBindings",
        "ffmpegCodecAndSoftwareRender", "headlessGodotBlenderSmoke",
        "kioskPhysicalClient", "ownedMediaRightsReview", "releaseApproval"
    ], "MACHINE_PROOF_LADDER")
    return source_receipts(root, EXPECTED_REFS)


def parse_kib_meminfo(text: str) -> dict:
    found: dict[str, int] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"(MemTotal|MemAvailable):\s+([0-9]{1,17}) kB\s*", line)
        if match:
            found[match.group(1)] = int(match.group(2)) * 1024
    return {"memTotalBytes": found.get("MemTotal"),
            "memAvailableBytes": found.get("MemAvailable")}


def parse_os_release(text: str) -> dict:
    # Do not evaluate shell scripts; allow only two bounded, sanitized fields.
    facts = {"distroId": None, "distroVersion": None}
    for line in text.splitlines():
        match = re.fullmatch(r"(ID|VERSION_ID)=\"?([A-Za-z0-9_.+~-]{1,80})\"?", line)
        if match:
            facts["distroId" if match.group(1) == "ID" else "distroVersion"] = match.group(2)
    return facts


def host_observe() -> dict:
    facts = {
        "system": platform.system(),
        "arch": platform.machine(),
        "kernelRelease": platform.release(),
        "logicalCpuCount": os.cpu_count(),
        "pageBytes": os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else None,
        "memTotalBytes": None, "memAvailableBytes": None,
        "distroId": None, "distroVersion": None,
    }
    if facts["system"] == "Linux":
        for name, parser in (("/etc/os-release", parse_os_release),
                             ("/proc/meminfo", parse_kib_meminfo)):
            try:
                path = Path(name)
                if path.is_file():
                    with path.open("rt", encoding="utf-8", errors="replace") as file:
                        facts.update(parser(file.read(8192)))
            except (OSError, UnicodeError, ValueError):
                pass
    return sanitize_facts(facts)


def sanitize_facts(facts: object) -> dict:
    require(type(facts) is dict and set(facts).issubset(SAFE_FACTS), "MACHINE_FACT_FIELDS")
    clean = dict.fromkeys(sorted(SAFE_FACTS))
    for k, v in facts.items():
        if k in ("logicalCpuCount", "pageBytes", "memTotalBytes", "memAvailableBytes"):
            require(v is None or (type(v) is int and 0 < v < (1 << 63)), "MACHINE_NUMERIC_FACT")
        else:
            require(v is None or (type(v) is str and SAFE_TEXT.fullmatch(v) is not None),
                    "MACHINE_STRING_FACT")
        clean[k] = v
    return clean


def software_presence() -> dict:
    # Never executes any software; shutil.which reads PATH only.
    return {tool: bool(shutil.which(tool)) for tool in TOOLS}


def sql_proof(source_rows: list[dict], facts: dict | None) -> dict:
    # STRICT is available in SQLite >=3.37.0, otherwise fail closed.
    with sqlite3.connect(":memory:") as conn:
        conn.execute("""CREATE TABLE machineSource (
          sequence INTEGER PRIMARY KEY CHECK(sequence BETWEEN 0 AND 127),
          name TEXT NOT NULL,
          byteCount INTEGER NOT NULL CHECK(byteCount BETWEEN 1 AND 1048576),
          sha256 TEXT NOT NULL CHECK(length(sha256)=64 AND sha256 NOT GLOB '*[^0-9a-f]*')
        ) STRICT""")
        for i, row in enumerate(source_rows):
            conn.execute("INSERT INTO machineSource VALUES(?,?,?,?)",
                         (i, row["source"], row["bytes"], row["sha256"]))
        rows = conn.execute("SELECT sequence,name FROM machineSource ORDER BY sequence").fetchall()
    return {"db": "SQLITE_MEMORY_STRICT", "records": len(rows),
            "sequence": [r[0] for r in rows], "externalDb": False, "hostWrite": False}


def snapshot(contract: dict, mode: str = "source", fixture: dict | None = None,
             root: Path = ROOT) -> dict:
    require(mode in ("source", "fixture", "host-read-only"), "MACHINE_MODE")
    source = check_contract(contract, root)
    if mode == "source":
        facts = None
        tools = None
    elif mode == "fixture":
        require(fixture is not None, "MACHINE_FIXTURE_MISSING")
        facts = sanitize_facts(fixture)
        tools = None
    else:
        require(fixture is None, "MACHINE_MODE_CONFLICT")
        facts = host_observe()
        tools = software_presence()
    sql = sql_proof(source, facts)
    return {
        "schema": "luhmOs.machineDebianSnapshotReceipt.v1",
        "contractSha256": hashlib.sha256(json.dumps(contract, sort_keys=True,
                               separators=(",", ":")).encode("utf-8")).hexdigest(),
        "verdict": "AMBER_SOURCE_ONLY" if mode == "source" else
                   "AMBER_SYNTHETIC_FIXTURE" if mode == "fixture" else "AMBER_HOST_OBSERVED",
        "mode": mode, "sourceFiles": source, "matrixCells": 16,
        "logicalHex": [f"0x{i:02X}" for i in range(16)],
        "linuxKernelIdentity": facts.get("kernelRelease") if facts else None,
        "hostEvidence": facts, "softwarePresence": tools, "sql": sql,
        "unverifiedGates": list(contract["nextGates"][1:]),
        "actualBackendDeployed": False, "physicalDeviceVerified": False,
        "kernelBuilt": False, "kernelModified": False, "bootloaderModified": False,
        "partitionModified": False, "emulatorRun": False, "ffmpegRendered": False,
        "machineSnapshotComplete": mode == "source", "runtimeSnapshotComplete": False,
        "crownStatus": "STOP",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--host-read-only", action="store_true",
                       help="Record coarse data on THIS host only, not proof of any other machine")
    group.add_argument("--fixture", type=Path,
                       help="Read a synthetic allowlisted fixture, NOT physical hardware proof")
    args = parser.parse_args()
    model = json.loads(CONTRACT.read_text(encoding="utf-8"))
    mode = "host-read-only" if args.host_read_only else "fixture" if args.fixture else "source"
    fixture = None
    if args.fixture:
        require(args.fixture.is_file() and args.fixture.stat().st_size <= 4096, "FIXTURE_FILE_LIMIT")
        fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    result = snapshot(model, mode, fixture)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
