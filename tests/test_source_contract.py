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

    def test_google_response_validation(self):
        self.assertIn("if not token:", self.source)
        self.assertIn("if len(results)!=1:", self.source)
        self.assertIn("if not media_id:", self.source)

    def test_control_command_validation(self):
        self.assertIn('if cmd not in ("pause","resume","cancel"):', self.source)
        self.assertIn('snapshot={**state,"logs":list(state["logs"])}', self.source)

    def test_queue_startup_failure_cleanup(self):
        self.assertIn("not ids or not all(", self.source)
        self.assertIn('app.logger.exception("Unable to start transfer worker")', self.source)
        self.assertIn('state["running"]=False', self.source)

    def test_large_file_memory_safety(self):
        self.assertIn("tempfile.SpooledTemporaryFile(", self.source)
        self.assertIn("raw.iter_content(chunk_size=1024*1024)", self.source)
        self.assertIn("upload_file.seek(0)", self.source)
        self.assertNotIn("data=raw.content", self.source)

    def test_private_response_headers(self):
        self.assertIn("@app.after_request", self.source)
        self.assertIn('response.headers["Cache-Control"]="no-store"', self.source)
        self.assertIn('response.headers["X-Content-Type-Options"]="nosniff"', self.source)
        self.assertIn('response.headers["X-Frame-Options"]="DENY"', self.source)
        self.assertIn('response.headers["Referrer-Policy"]="no-referrer"', self.source)

    def test_secrets_not_hardcoded(self):
        self.assertIn('os.getenv("IMMICH_API_KEY"', self.source)
        self.assertNotIn("AIza", self.source)

if __name__ == "__main__":
    unittest.main()
