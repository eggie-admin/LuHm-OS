"""SQL-first runtime reads, reviewed YAML fallback, zero Markdown runtime parsing."""
import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "doctrine/statePrecedenceV1.yaml"
SOURCE = ROOT / "host/api/stateResolution.py"
SPEC = importlib.util.spec_from_file_location("luhmStateResolution", SOURCE)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
SHA = "a" * 40

def memoryDb():
    db = sqlite3.connect(":memory:")
    db.execute(
        "CREATE TABLE luhm_runtime_state (namespace TEXT NOT NULL, "
        "state_key TEXT NOT NULL, value_json TEXT NOT NULL, "
        "status TEXT NOT NULL, source_sha TEXT NOT NULL, "
        "PRIMARY KEY(namespace,state_key))"
    )
    return db

class SqlFirstStateTests(unittest.TestCase):
    def test_real_reviewed_yaml_is_safe_and_structured(self):
        d=mod.readReviewedYaml(CONFIG)
        self.assertEqual(d["lookup"]["order"],[
            "sqlDatabase","yamlDefaults","markdownRecoveryOnly"])
        self.assertFalse(d["lookup"]["markdownRecoveryOnly"]["runtimeMachineAuthority"])
        self.assertFalse(d["lookup"]["markdownRecoveryOnly"]["neverParsedAsRuntimeConfig"] is False)
        self.assertTrue(d["lookup"]["sqlDatabase"]["publicPorts"] is False)

    def test_sql_value_overrides_reviewed_yaml_for_ui_only(self):
        with memoryDb() as db:
            db.execute("INSERT INTO luhm_runtime_state VALUES (?,?,?,?,?)",
                       ("luhm","ui.theme",'"light"',"active",SHA))
            result=mod.resolveState(db,"ui.theme",CONFIG,SHA,backend="sqlite")
            self.assertEqual(result,{"value":"light","source":"sqlDatabase","degraded":False})

    def test_missing_sql_row_uses_reviewed_yaml(self):
        with memoryDb() as db:
            value=mod.resolveState(db,"ui.theme",CONFIG,SHA,backend="sqlite")
            self.assertEqual(value,{"value":"dark","source":"yamlDefaults","degraded":False})

    def test_empty_database_requires_explicit_degraded_permission(self):
        with self.assertRaisesRegex(mod.StateResolutionError,"RED_EXISTING_DATABASE_REQUIRED"):
            mod.resolveState(None,"ui.theme",CONFIG,SHA)
        self.assertEqual(mod.resolveState(None,"ui.theme",CONFIG,SHA,allowOfflineUi=True)["degraded"],True)

    def test_outage_fails_closed_unless_only_ui_degradation_is_explicit(self):
        db=memoryDb();db.close()
        with self.assertRaisesRegex(mod.StateResolutionError,"RED_DATABASE_QUERY_FAILED"):
            mod.resolveState(db,"ui.motion",CONFIG,SHA,backend="sqlite")
        result=mod.resolveState(db,"ui.motion",CONFIG,SHA,backend="sqlite",allowOfflineUi=True)
        self.assertEqual(result["value"],"reduced")
        self.assertTrue(result["degraded"])

    def test_revoked_row_never_resurfaces_yaml_fallback(self):
        with memoryDb() as db:
            db.execute("INSERT INTO luhm_runtime_state VALUES (?,?,?,?,?)",
                       ("luhm","ui.theme",'"light"',"revoked",SHA))
            with self.assertRaisesRegex(mod.StateResolutionError,"RED_DATABASE_ENTRY_REVOKED"):
                mod.resolveState(db,"ui.theme",CONFIG,SHA,backend="sqlite",allowOfflineUi=True)

    def test_wrong_revision_rejected_instead_of_automatic_sql_authority(self):
        with memoryDb() as db:
            db.execute("INSERT INTO luhm_runtime_state VALUES (?,?,?,?,?)",
                       ("luhm","ui.theme",'"light"',"active","b"*40))
            with self.assertRaisesRegex(mod.StateResolutionError,"RED_DATABASE_DOCTRINE_REVISION_CONFLICT"):
                mod.resolveState(db,"ui.theme",CONFIG,SHA,backend="sqlite")

    def test_no_crown_or_auth_keys_as_fallback(self):
        with memoryDb() as db:
            for key in ("crownAuthority","authentication","ui.password","signingKeys"):
                with self.assertRaisesRegex(mod.StateResolutionError,"RED_NON_WHITELISTED_KEY"):
                    mod.resolveState(db,key,CONFIG,SHA,backend="sqlite",allowOfflineUi=True)

    def test_unknown_sql_enum_cannot_override_yaml(self):
        with memoryDb() as db:
            db.execute("INSERT INTO luhm_runtime_state VALUES (?,?,?,?,?)",
                       ("luhm","ui.theme",'"malicious"',"active",SHA))
            with self.assertRaisesRegex(mod.StateResolutionError,"RED_SQL_VALUE_OUTSIDE_BOUNDS"):
                mod.resolveState(db,"ui.theme",CONFIG,SHA,backend="sqlite")

    def test_python_yaml_tags_not_executed(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"reviewed.yaml"
            p.write_text("!!python/object/apply:os.system ['echo unwanted']",encoding="utf-8")
            with self.assertRaisesRegex(mod.StateResolutionError,"RED_YAML_CONFIG_UNAVAILABLE_OR_UNSAFE"):
                mod.resolveState(None,"ui.theme",p,SHA,allowOfflineUi=True)

    def test_sql_source_is_not_auto_apply(self):
        sql=(ROOT/"host/api/stateResolutionV1.sql").read_text(encoding="utf-8")
        self.assertIn("EXISTING Professor-approved",sql)
        self.assertIn("unix socket",sql.lower())
        self.assertIn("luhm_runtime_state",sql)
        self.assertIn("luhm_state_event",sql)
        self.assertNotIn("DROP TABLE",sql)
        self.assertNotIn("GRANT ALL",sql)

if __name__=="__main__":
    unittest.main()
