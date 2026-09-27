"""Negative controls: reject changed inputs, missing output and corrupt cache."""
import importlib.util
import json
from pathlib import Path
import tempfile
import hashlib
spec = importlib.util.spec_from_file_location('moduleBuild', Path(__file__).resolve().parents[1]/'tools/moduleBuild.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as tmp:
    cache, out = Path(tmp)/'cache', Path(tmp)/'out'
    cache.mkdir()
    hashes = {}
    for name in m.OUTPUTS:
        data = ('fixture-'+name).encode()
        (cache/name).write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    (cache/'receipt.json').write_text(json.dumps({'input_sha256':'expected','outputs':hashes}))
    assert not m.restore(cache,out,'changed')
    assert not out.exists()
    assert m.restore(cache,out,'expected')
    (cache/m.OUTPUTS[0]).write_bytes(b'corruption')
    assert not m.restore(cache,out,'expected')
    (cache/m.OUTPUTS[0]).unlink()
    assert not m.restore(cache,out,'expected')
    (cache/'receipt.json').write_text('{}')
    assert not m.restore(cache,out,'expected')
print('MODULE_CACHE_NEGATIVE_CONTROLS=PASS')
