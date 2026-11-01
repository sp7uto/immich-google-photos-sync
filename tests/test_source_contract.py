"""Offline tests for the published source; no credentials or network required."""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVER = ROOT / "app" / "app.py"
HTML = ROOT / "app" / "templates" / "index.html"

class SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SERVER.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.html = HTML.read_text(encoding="utf-8")

    def test_required_routes(self):
        routes = set()
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for d in node.decorator_list:
                    if isinstance(d, ast.Call) and d.args and isinstance(d.args[0], ast.Constant):
                        if isinstance(d.func, ast.Attribute) and d.func.attr in ("get", "post", "route"):
                            routes.add(d.args[0].value)
        self.assertTrue({"/", "/api/preview", "/api/send", "/api/status", "/api/history.csv"} <= routes)

    def test_manual_selection_and_confirmation(self):
        self.assertIn("data-id=", self.html)
        self.assertIn("confirm(", self.html)
        self.assertIn('request.get_json(silent=True)', self.source)

    def test_queue_lock_and_failure_cleanup(self):
        self.assertIn('with lock:\n        if state["running"]:', self.source)
        self.assertIn('finally:\n        with lock:', self.source)

    def test_filename_escaping_and_status_safety(self):
        self.assertIn("escapeHtml(x.name)", self.html)
        self.assertIn("escapeHtml(x.id)", self.html)
        self.assertIn("cur.textContent=", self.html)
        self.assertNotIn("cur.innerHTML=", self.html)

    def test_secrets_not_hardcoded(self):
        self.assertIn('os.getenv("IMMICH_API_KEY"', self.source)
        self.assertNotIn("AIza", self.source)

if __name__ == "__main__":
    unittest.main()
