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

    def test_optional_panel_authentication(self):
        self.assertIn("@app.before_request", self.source)
        self.assertIn('PANEL_PASSWORD=os.getenv("PANEL_PASSWORD","")', self.source)
        self.assertIn("hmac.compare_digest(", self.source)
        self.assertIn('"WWW-Authenticate"', self.source)

    def test_cross_origin_write_guard(self):
        self.assertIn("def reject_cross_origin_writes():", self.source)
        self.assertIn('request.method not in ("POST","PUT","PATCH","DELETE")', self.source)
        self.assertIn('request.headers.get("Sec-Fetch-Site","")', self.source)
        self.assertIn('request.headers.get("Origin")', self.source)
        self.assertIn('"Cross-origin request blocked"', self.source)

    def test_atomic_oauth_token_writes(self):
        helper=(ROOT / "get_google_token.py").read_text(encoding="utf-8")
        for source in (self.source, helper):
            self.assertIn("tempfile.mkstemp(", source)
            self.assertIn("os.fchmod(fd", source)
            self.assertIn("os.fsync(output.fileno())", source)
            self.assertIn("os.replace(temporary", source)
        self.assertNotIn('(DATA/"token.json").write_text(', self.source)

    def test_configuration_validation(self):
        self.assertIn("changes=request.get_json(silent=True)", self.source)
        self.assertIn("if set(changes)-allowed:", self.source)
        self.assertIn('if key=="post_action" and value!="keep":', self.source)

    def test_atomic_configuration_and_control_header(self):
        self.assertIn('tempfile.mkstemp(prefix=".config-"', self.source)
        self.assertIn("os.replace(temporary,CFG)", self.source)
        self.assertIn('request.headers.get("X-Requested-With")!="XMLHttpRequest"', self.source)
        self.assertIn("'X-Requested-With':'XMLHttpRequest'", self.html)

    def test_auth_failure_cooldown(self):
        self.assertIn("AUTH_MAX_FAILURES=5", self.source)
        self.assertIn("AUTH_WINDOW_SECONDS=60", self.source)
        self.assertIn("AUTH_LOCK_SECONDS=60", self.source)
        self.assertIn("time.monotonic()", self.source)
        self.assertIn("with _auth_lock:", self.source)
        self.assertIn('Response("Too many authentication attempts",429', self.source)

    def test_optional_nonroot_override(self):
        override=(ROOT / "docker-compose.nonroot.yml").read_text(encoding="utf-8")
        base=(ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("APP_UID", override)
        self.assertIn("APP_GID", override)
        self.assertIn("read_only: true", override)
        self.assertIn("no-new-privileges:true", override)
        self.assertIn("cap_drop:", override)
        self.assertNotIn("read_only: true", base)

    def test_ci_does_not_run_simulated_containers(self):
        workflow=(ROOT / ".github" / "workflows" / "check.yml").read_text(encoding="utf-8")
        self.assertIn("docker build --tag immich-google-sync:ci .", workflow)
        self.assertNotIn("docker run ", workflow)
        self.assertNotIn("docker-smoke:", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)

    def test_backup_is_protected_write(self):
        self.assertIn('@app.post("/api/backup")', self.source)
        self.assertNotIn('@app.get("/api/backup")', self.source)
        self.assertIn("fetch('/api/backup',{method:'POST'", self.html)
        self.assertIn('request.headers.get("X-Requested-With")!="XMLHttpRequest"', self.source)

    def test_uncertain_uploads_are_not_retried(self):
        self.assertIn("status in ('sent','uploading','needs_review')", self.source)
        self.assertIn("status='needs_review'", self.source)
        self.assertIn("mid=google_upload(a,c", self.source)
        self.assertIn("statuses=transfer_statuses()", self.source)
        self.assertIn('id="review"', self.html)
        self.assertIn("x.sent||x.review", self.html)

    def test_secrets_not_hardcoded(self):
        self.assertIn('os.getenv("IMMICH_API_KEY"', self.source)
        self.assertNotIn("AIza", self.source)

if __name__ == "__main__":
    unittest.main()
