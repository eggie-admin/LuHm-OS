import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("inChatHtmlCheck", Path(__file__).parents[1] / "tools" / "inChatHtmlCheck.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def write_html(text: str) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
    handle.write(text)
    handle.close()
    return Path(handle.name)


GOOD = """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>x</title><link rel='stylesheet' href='./x.css'></head><body><main data-luhm-cockpit><button id='b' type='button'>x</button></main><script src='./jquery-3.7.1.min.js'></script><script src='./app.js'></script></body></html>"""


class HtmlCheckTests(unittest.TestCase):
    def test_good_contract_is_green(self):
        receipt = MOD.check(write_html(GOOD))
        self.assertEqual(receipt["status"], "GREEN_STATIC_HTML")
        self.assertEqual(receipt["failures"], [])

    def test_inline_handler_is_red(self):
        receipt = MOD.check(write_html(GOOD.replace("type='button'", "type='button' onclick='x()'")))
        self.assertIn("inline_event_handlers", receipt["failures"])

    def test_external_asset_is_red(self):
        receipt = MOD.check(write_html(GOOD.replace("./x.css", "https://example.invalid/x.css")))
        self.assertIn("external_http_asset", receipt["failures"])

    def test_network_primitive_is_red(self):
        receipt = MOD.check(write_html(GOOD.replace("</main>", "<script>fetch('/x')</script></main>")))
        self.assertIn("network_primitive_in_html", receipt["failures"])

    def test_dangerous_sink_is_red(self):
        receipt = MOD.check(write_html(GOOD.replace("</main>", "<script>node.innerHTML='x'</script></main>")))
        self.assertIn("dangerous_dom_sink_in_html", receipt["failures"])

    def test_bad_script_order_is_red(self):
        bad = GOOD.replace("<script src='./jquery-3.7.1.min.js'></script><script src='./app.js'></script>", "<script src='./app.js'></script><script src='./jquery-3.7.1.min.js'></script>")
        receipt = MOD.check(write_html(bad))
        self.assertIn("script_order", receipt["failures"])


if __name__ == "__main__":
    unittest.main()
