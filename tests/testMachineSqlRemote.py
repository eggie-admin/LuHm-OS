import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("machineSqlRemote",ROOT/"host/api/machineSqlRemote.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class RemoteConfigTests(unittest.TestCase):
    def test_refuses_unselected_runtime(self):
        with self.assertRaises(mod.MachineLayerError):
            mod.validateRemoteEnvironment({})
    def test_tls_downgrade_refused(self):
        with tempfile.TemporaryDirectory() as dir:
            cert=Path(dir)/"ca.pem"
            cert.write_text("not a real CA, config validation only")
            environment={"LUHM_REMOTE_SQL_SYNC":"scopedSourceTxRx","LUHM_DATABASE_URL":f"postgresql://user:testpassword@localhost/test?sslmode=require&sslrootcert={cert}"}
            with self.assertRaises(mod.MachineLayerError): mod.validateRemoteEnvironment(environment)
    def test_no_username_or_password_refused(self):
        with tempfile.TemporaryDirectory() as dir:
            cert=Path(dir)/"ca.pem"
            cert.write_text("test fixture")
            environment={"LUHM_REMOTE_SQL_SYNC":"scopedSourceTxRx","LUHM_DATABASE_URL":f"postgresql://localhost/test?sslmode=verify-full&sslrootcert={cert}"}
            with self.assertRaises(mod.MachineLayerError): mod.validateRemoteEnvironment(environment)
    def test_verified_config_does_not_connect(self):
        with tempfile.TemporaryDirectory() as dir:
            cert=Path(dir)/"ca.pem"
            cert.write_text("test fixture")
            url=f"postgresql://app:password@db.example.invalid/test?sslmode=verify-full&sslrootcert={cert}"
            environment={"LUHM_REMOTE_SQL_SYNC":"scopedSourceTxRx","LUHM_DATABASE_URL":url}
            self.assertEqual(mod.validateRemoteEnvironment(environment),url)
