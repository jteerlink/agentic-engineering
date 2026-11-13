"""The Router against a local stub of the gateway's decisions endpoint (gateway docs, api/decisions)."""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROUTER = Path(__file__).resolve().parent.parent / "router" / "jev_router.py"
TASK = {"prompt": "Find all API endpoints", "description": "Find API endpoints", "subagent_type": "Explore"}
PLANTED = [
    "sk-ant-FAKE0000000000000000000000",
    "ghp_FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE12",
    "AKIAFAKEFAKEFAKEFAKE",
    "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmYWtlIn0.ZmFrZXNpZ25hdHVyZQ",
    "s3cretFAKEpassw0rd",
]


class Stub(BaseHTTPRequestHandler):
    received, mode, choice, confidence = [], "ok", "haiku", 0.8

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        Stub.received.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body.decode()})
        if Stub.mode == "500":
            self.send_response(500); self.end_headers(); return
        if Stub.mode == "hang":
            time.sleep(6)
        name = next(iter(json.loads(body)["questions"]))
        answer = {"type": "choice", "choice": Stub.choice, "confidence": Stub.confidence,
                  "probabilities": {Stub.choice: 0.9, "other": 0.1}}
        out = b"{not json" if Stub.mode == "badjson" else json.dumps(
            {"model": "jev-1.13.0", "answers": {name: answer}, "usage": {}}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(out)

    def log_message(self, format, *args):
        pass


class Router(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        Stub.received, Stub.mode, Stub.choice, Stub.confidence = [], "ok", "haiku", 0.8
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name, "home")
        self.cwd = Path(self.tmp.name, "repo")
        self.home.mkdir(); self.cwd.mkdir()
        self.log = self.home / ".local/state/jev-router/decisions.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def run_router(self, tool_input=None, tool="Agent", key: str | None = "testkey", **env):
        e = {k: v for k, v in os.environ.items() if not k.startswith(("AIGW_", "JEV_", "ANTHROPIC_"))}
        e.update(HOME=str(self.home), AIGW_BASE=self.url)
        if key:
            e["AIGW_API_KEY"] = key
        e.update(env)
        payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": str(self.cwd),
                              "tool_input": TASK if tool_input is None else tool_input})
        r = subprocess.run([sys.executable, str(ROUTER)], input=payload, capture_output=True, text=True, env=e, timeout=20)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def hook_output(self, out):
        self.assertTrue(out, "the Router printed nothing")
        return json.loads(out)["hookSpecificOutput"]

    def log_lines(self):
        self.assertTrue(self.log.exists(), f"no log at {self.log}")
        return [json.loads(l) for l in self.log.read_text().splitlines()]

    def test_rewrites_unset_model(self):
        h = self.hook_output(self.run_router())
        self.assertEqual(h["hookEventName"], "PreToolUse")
        self.assertEqual(h["permissionDecision"], "allow")
        self.assertEqual(h["updatedInput"], {**TASK, "model": "haiku"})

    def test_low_confidence_goes_one_model_up(self):
        for pick, conf, want in [("haiku", 0.4, "sonnet"), ("sonnet", 0.4, "opus"), ("opus", 0.4, "opus"), ("sonnet", 0.5, "sonnet")]:
            with self.subTest(pick=pick, conf=conf):
                Stub.choice, Stub.confidence = pick, conf
                self.assertEqual(self.hook_output(self.run_router())["updatedInput"]["model"], want)

    def test_skip_explicit_choices(self):
        agents = self.cwd / ".claude/agents"
        agents.mkdir(parents=True)
        (agents / "pinned.md").write_text("---\nname: pinned\nmodel: sonnet\n---\n# Pinned\n")
        (agents / "unpinned.md").write_text("---\nname: unpinned\ntools: Read\n---\nmodel: not frontmatter\n")
        cases = {"call sets model": {**TASK, "model": "opus"}, "agent file sets model": {**TASK, "subagent_type": "pinned"},
                 "fork": {**TASK, "subagent_type": "fork"}, "plugin agent": {**TASK, "subagent_type": "my-plugin:reviewer"}}
        for name, task in cases.items():
            with self.subTest(name):
                Stub.received = []
                self.assertEqual(self.run_router(task), "")
                self.assertEqual(Stub.received, [], "a skipped call must not reach Jev")
        skips = [l for l in self.log_lines() if l["action"] == "skip"]
        self.assertEqual(len(skips), len(cases), "each skip needs a log line with its reason")
        self.assertTrue(all(l.get("reason") for l in skips))
        Stub.received = []
        self.assertEqual(self.run_router(TASK, tool="Bash"), "")
        self.assertEqual(Stub.received, [])
        self.assertTrue(self.hook_output(self.run_router({**TASK, "subagent_type": "unpinned"})), "an agent file without a model is routed")

    def test_request_shape(self):
        self.run_router()
        self.assertEqual(len(Stub.received), 1, "no request reached the gateway")
        req = Stub.received[0]
        body = json.loads(req["body"])
        self.assertEqual(req["path"], "/v1/decisions")
        self.assertEqual(req["auth"], "Bearer testkey")
        self.assertEqual(set(body), {"model", "state", "questions"})
        self.assertEqual(body["model"], "jev")
        [q] = body["questions"].values()
        self.assertEqual(q["type"], "choice")
        self.assertEqual(set(q["criteria"]), {"haiku", "sonnet", "opus"})
        self.assertEqual(body["state"], {"subagent_type": "Explore", "prompt": "Find all API endpoints"})
        Stub.received = []
        self.run_router(AIGW_BASE="", ANTHROPIC_BASE_URL=self.url)
        self.assertEqual(len(Stub.received), 1, "ANTHROPIC_BASE_URL not used when AIGW_BASE is unset")
        Stub.received = []
        self.run_router(ANTHROPIC_BASE_URL="http://127.0.0.1:9")
        self.assertEqual(len(Stub.received), 1, "AIGW_BASE must win over ANTHROPIC_BASE_URL")

    def test_egress_redacts_and_truncates(self):
        prompt = "Use these: " + " ".join(PLANTED[:4]) + f" password={PLANTED[4]} " + "x " * 5000
        self.run_router({**TASK, "prompt": prompt})
        self.assertEqual(len(Stub.received), 1, "no request reached the gateway")
        body = Stub.received[0]["body"]
        for secret in PLANTED:
            self.assertNotIn(secret, body)
        self.assertLessEqual(len(json.loads(body)["state"]["prompt"]), 4000)

    def test_fail_silent(self):
        for mode in ("500", "badjson", "hang"):
            with self.subTest(mode):
                Stub.mode = mode
                self.assertEqual(self.run_router(), "")
        Stub.mode = "ok"
        self.assertEqual(self.run_router(key=None), "")

    def test_off_switch_skips(self):
        Stub.received = []
        self.assertEqual(self.run_router(JEV_ROUTER_OFF="1"), "")
        self.assertEqual(Stub.received, [], "the off switch must not reach Jev")
        self.assertEqual(self.log_lines()[0]["reason"], "disabled by JEV_ROUTER_OFF")

    def test_log_line_per_decision(self):
        self.run_router()
        [line] = self.log_lines()
        for field in ("time", "cwd", "subagent_type", "action", "pick", "model", "confidence", "probabilities"):
            self.assertIn(field, line)
        self.assertEqual((line["action"], line["pick"], line["model"], line["subagent_type"]), ("route", "haiku", "haiku", "Explore"))
        self.assertNotIn("Find all API endpoints", self.log.read_text())


if __name__ == "__main__":
    unittest.main()
