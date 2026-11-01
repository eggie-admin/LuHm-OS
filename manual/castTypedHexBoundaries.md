# CAST Typed Security Boundaries: four-by-four from firmware to application

**Status:** source-only candidate; no privileged actions. Canonical main observed `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`. This adds a *separate typed audit coordinate namespace*, `castSecurityMatrixV1`; it does not replace the Goddess Song 4×4 snapshot (draft PR #469), approve that draft, or create a new OS-level privilege. It extends the existing Machine-to-Human Wizard audit.

## The meaning of hex

- Hexadecimal is a readable base-16 notation for integers, byte arrays and hashes. It is **not** an access-control mechanism. All `0x00..0x0F` values here are **symbolic matrix cell indexes** in this schema's own namespace. They are not Android partitions, CPU page permissions, Linux flags, USB IDs, MAC addresses, or firmware offsets.
- These four synthetic *audit-only* bit flags have disjoint meanings: `0x01` = Git SHA syntax accepted; `0x02` = supplied **synthetic byte payload** matched its SHA-256 digest; `0x04` = a declared boundary class was selected; `0x08` = external human release receipt, **never** set by this tool. `0x07` means source-only checks, not privileged authorization. Even `0x0F` would not grant capabilities absent independently enforced system and owner gates.
- IEEE-754 float bit patterns, signed integer hex, fixed-point scaled integers, bus vendor/device identifiers, IPv6 addresses (128-bit), Git object names and SHA-256 digests have different semantics. Equal hex digits do not prove any relationship. Use explicit typed joins and attested evidence.

## Four independent enforcement rows × four evidence columns

| Row | Actual enforcement authority | Source-level proof we can hold | What is not proven |
| --- | --- | --- | --- |
| Firmware | OEM immutable/managed root of trust, **Android Verified Boot**, rollback protection | `doctrine/machineToHumanWizardV1.json` | Current Samsung boot state, private signing algorithm, key or firmware writes |
| Kernel | Linux access control and, on Android, **SELinux** enforcing domains | `tools/machineToHumanWizard.py` | Kernel module loaded, SELinux domain labels on physical tablet |
| Network | Verified firewall/ACL, correct IPv6 scope, TLS plus authenticated/authorized origin | `doctrine/cloudflareEdgeHardeningV1.json` | IPv6 prefix by itself grants access, any currently approved AAAA or public port |
| Application | Typed task manifest, exact commit/CI, optional Android app signatures, owner review | `doctrine/companyWideOperationalQuarantineV1.json` | Agent activation, protected-main merge, signed APK, public deployment |

Each row passes through **Identify → Verify → Enforce → Escalate**, but a cell records **source routing**, not successful runtime enforcement. The next conceptual 8×8/16×16 levels are reserved with **zero verified runtime cells**.

### ECDSA and IPv6 are not an escalation ladder

**ECDSA** (NIST FIPS 186-5) verifies a signature under an identified public key and algorithm. It does **not** create authorization or necessarily describe every Android/Samsung boot signature. AVB algorithms, root keys and rollback metadata are OEM/version-specific. Correct trust needs both verified signature/identity and the separate policy that allows the resulting action.

**IPv6** (RFC 4291) encodes 128-bit addresses and prefix lengths for routing/subnets. `2001:db8::/32` is for documentation, `::1/128` loopback, `fe80::/10` link-local. Prefix parsing **does not** configure a firewall, establish TLS, issue auth tokens or verify a network origin. Existing Cloudflare source policy forbids inferred AAAA records and accidental LAN exposure.

## Debian and studio inheritance

The main `.devcontainer/Dockerfile` declares Ubuntu userland `apt-get` packages, Python/SQLite, Node/npm, Blender, FFmpeg and Godot; it **does not own the provider's Codespaces kernel**. Actual module binding requires a read-only observation from the right physical host, matching bus modalias, kernel version, firmware and package provenance. No dpkg package or driver update is authorized by discovering a hex ID. The package build and studio proof remain separate.

### Local reproduction

```bash
python3 -m unittest discover -s tests -p 'testCastTypedHexBoundaries.py' -v
python3 tools/castTypedHexBoundaries.py --self-test
python3 -m unittest discover -s tests -p 'testMachineToHumanWizard.py' -v
```

All negative controls run offline; no networking, device probing, firewall changes, root escalation, agent workers or ROM/firmware writes.

Official technical references: Android AVB `https://source.android.com/docs/security/features/verifiedboot`; Android SELinux `https://source.android.com/docs/security/features/selinux`; NIST DSS `https://csrc.nist.gov/pubs/fips/186-5/final`; IPv6 architecture `https://www.rfc-editor.org/rfc/rfc4291`.

**Governance:** AI proposes. Policy authorizes. CI proves. Human promotes. CROWN STOP.
