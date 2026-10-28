#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,Mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("mediaPreview",ROOT/"tools/premonitionMediaPreview.py")
media=importlib.util.module_from_spec(spec)
spec.loader.exec_module(media)

class MediaTests(unittest.TestCase):
 def testSafeMediaAndScopedFiles(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/"good.mp4").write_bytes(b"test-bytes")
   self.assertEqual(media.safeMediaPath(root,"good.mp4"),root/"good.mp4")
   for name in ("../good.mp4","https://example.com/stream.mp4","/etc/passwd","file:///tmp/x.mp4","file.txt"):
    with self.subTest(name=name),self.assertRaises((ValueError,FileNotFoundError)):
     media.safeMediaPath(root,name)
 def testSymlinkEscapeDenied(self):
  with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
   root=Path(tmp);external=Path(other)/"out.mp4";external.write_bytes(b"x")
   (root/"escape.mp4").symlink_to(external)
   with self.assertRaises(ValueError):media.safeMediaPath(root,"escape.mp4")
 def testMetadataReadDoesNotClaimPlayback(self):
  with tempfile.TemporaryDirectory() as tmp:
   file=Path(tmp)/"real.mp4";file.write_bytes(b"video")
   mock=Mock(returncode=0,stdout=json.dumps({"streams":[{"codec_type":"video","codec_name":"h264"}],"format":{"duration":"1.0"}}))
   with patch.object(media.subprocess,"run",return_value=mock) as proc:
    receipt=media.inspectMedia(file,probeExe="/usr/bin/ffprobe")
   self.assertEqual(receipt["streams"][0]["codec"],"h264")
   self.assertFalse(receipt["playbackVerified"])
   self.assertEqual(receipt["crownStatus"],"STOP")
   proc.assert_called_once()
   self.assertEqual(proc.call_args.kwargs["timeout"],12)
 def testVlcNeverLaunchesUnarmed(self):
  with patch.object(media.subprocess,"Popen") as proc:
   with self.assertRaises(ValueError):media.playVlc(Path("/tmp/media.mp4"),armed=False,vlcExe="/usr/bin/vlc")
   proc.assert_not_called()
 def testArmedVlcOnlyOpensLocalPathNoHttpMode(self):
  with patch.object(media.subprocess,"Popen",return_value=Mock(pid=4321)) as proc:
   self.assertEqual(media.playVlc(Path("/tmp/media.mp4"),armed=True,vlcExe="/usr/bin/vlc"),4321)
   argv=proc.call_args.args[0]
   self.assertTrue(argv[-1].endswith("media.mp4"))
   self.assertNotIn("http",str(argv).lower())
if __name__=="__main__":unittest.main()
