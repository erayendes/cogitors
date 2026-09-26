"""Offline runner checks; fake executables never contact model providers."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch


RUNNER = Path(__file__).resolve().parents[1] / "skills/cogitors/scripts/run.py"
FAKE = r'''
import json, os, pathlib, subprocess, sys, time
agent = pathlib.Path(sys.argv[0]).name
root = pathlib.Path(os.environ["COGITOR_TEST_ROOT"])
if agent == "claude" and sys.argv[1:] == ["auth", "status"]:
    print(json.dumps({"loggedIn": os.environ.get("COGITOR_TEST_AUTH", "yes") == "yes"}))
    sys.exit(0)
if agent == "codex" and sys.argv[1:] == ["login", "status"]:
    sys.exit(0)
prompt = sys.argv[sys.argv.index("-p") + 1] if agent == "agy" else sys.stdin.read()
task = prompt.rsplit("\n\n", 1)[-1]
(root / (agent + ".started")).write_text(json.dumps({"cwd": os.getcwd(), "prompt": prompt, "args": sys.argv[1:]}))
if task in ("timeout", "interrupt"):
    child = subprocess.Popen([sys.executable, "-c", "import pathlib,sys,time; time.sleep(1.1); pathlib.Path(sys.argv[1]).touch()", str(root / "orphan-survived")])
    (root / "child.pid").write_text(str(child.pid))
    time.sleep(30)
elif task == "overlap":
    deadline = time.monotonic() + 3
    while len(list(root.glob("*.started"))) < 3:
        if time.monotonic() > deadline:
            sys.exit(19)
        time.sleep(.01)
if task == "malformed":
    print("not json")
elif task == "unknown":
    print(json.dumps({"unexpected": "schema"}))
elif task == "duplicate":
    print('{"status":"SUCCESS","status":"SUCCESS"}')
elif agent == "codex":
    print(json.dumps({"type": "thread.started", "thread_id": "codex-session"}))
    print(json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "codex response"}}))
    event = {"type": "turn.failed"} if task == "json-error" else {"type": "turn.completed"}
    if task != "no-usage": event["usage"] = {"input_tokens": 5}
    print(json.dumps(event))
elif agent == "claude":
    result = {"subtype": "error_during_execution" if task == "json-error" else "success", "is_error": task == "json-error", "result": "claude response", "session_id": "claude-session"}
    if task != "no-usage": result["usage"] = {"input_tokens": 6}
    print(json.dumps(result))
else:
    print(json.dumps({"status": "ERROR" if task == "json-error" else "SUCCESS", "response": "agy response", "conversation_id": "agy-session"}))
print("retained stderr", file=sys.stderr)
if task == "nonzero": sys.exit(7)
'''


class RunnerCheck(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cogitor-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.env = dict(os.environ, PATH=str(self.bin), COGITOR_TEST_ROOT=str(self.root),
                        TMPDIR=str(self.root), PYTHONDONTWRITEBYTECODE="1")
        for name in ("codex", "claude", "agy"):
            executable = self.bin / name
            executable.write_text("#!" + sys.executable + "\n" + FAKE, encoding="utf-8")
            executable.chmod(0o700)
        self.manifest = self.root / "jobs.json"

    def runner(self):
        self.assertTrue(RUNNER.is_file(), "reusable runner has not been implemented")
        spec = importlib.util.spec_from_file_location("cogitor_runner", RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def jobs(self, prompt="ok"):
        return [dict(agent=agent, cwd=str(self.root), prompt=prompt, timeout_seconds=5)
                for agent in ("codex", "claude", "antigravity")]

    def invoke(self, jobs):
        self.manifest.write_text(json.dumps({"jobs": jobs}), encoding="utf-8")
        # Fake CLIs cannot exercise a real language server; isolate only that OS probe.
        bootstrap = ("import sys; sys.path.insert(0, sys.argv.pop(1)); import run; "
                     "from unittest.mock import patch; "
                     "patch.object(run, 'probe_antigravity').start(); sys.exit(run.main())")
        return subprocess.run([sys.executable, "-c", bootstrap, str(RUNNER.parent), str(self.manifest)],
                              env=self.env, capture_output=True, text=True, timeout=12)

    def results(self, completed):
        summary = json.loads(completed.stdout)
        self.assertNotIn("response", completed.stdout)
        self.assertEqual(Path(summary["results_dir"]).stat().st_mode & 0o077, 0)
        results = [json.loads(Path(job["result_path"]).read_text()) for job in summary["jobs"]]
        for result in results:
            for key in ("stdout_path", "stderr_path", "result_path"):
                path = Path(result[key])
                self.assertTrue(path.is_absolute())
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_mode & 0o077, 0)
            self.assertEqual(len(result["request_hash"]), 64)
        return results

    def started(self, name):
        return json.loads((self.root / (name + ".started")).read_text())

    def test_parallel_success_and_usage_absence(self):
        completed = self.invoke(self.jobs("overlap"))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        results = self.results(completed)
        self.assertEqual([r["session_id"] for r in results],
                         ["codex-session", "claude-session", "agy-session"])
        self.assertTrue(all(r["status"] == "success" for r in results))
        self.assertTrue(all(r["model"] is None and r["effort"] is None for r in results))
        completed = self.invoke(self.jobs("no-usage"))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(all(r["usage"] is None for r in self.results(completed)))

    def test_preflight_detects_hidden_auth_before_starting_any_model(self):
        runner = self.runner()
        self.assertTrue(hasattr(runner, "preflight"), "missing no-model readiness gate")
        with patch.dict(os.environ, dict(self.env, COGITOR_TEST_AUTH="no"), clear=True):
            with self.assertRaisesRegex(ValueError, "auth|logged|permission"):
                runner.preflight(self.jobs()[:2])
        self.assertFalse(list(self.root.glob("*.started")))
        with patch.dict(os.environ, self.env, clear=True):
            runner.preflight(self.jobs()[:2])
        self.assertFalse(list(self.root.glob("*.started")))

    def test_preflight_reports_blocked_local_port_without_model_call(self):
        runner = self.runner()
        self.assertTrue(hasattr(runner, "preflight"), "missing no-model readiness gate")
        with patch.dict(os.environ, self.env, clear=True):
            with patch.object(runner.socket, "socket", side_effect=PermissionError("bind denied")):
                with self.assertRaisesRegex(ValueError, "permission|sandbox|bind"):
                    runner.preflight(self.jobs()[2:])
        self.assertFalse(list(self.root.glob("*.started")))

    def test_literal_prompt_and_nonrecursive_guard_for_every_provider(self):
        sentinel = self.root / "shell-was-used"
        prompt = "quotes ' \" ; $(touch %s) `touch %s`\n$HOME" % (sentinel, sentinel)
        completed = self.invoke(self.jobs(prompt))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        for executable in ("codex", "claude", "agy"):
            started = self.started(executable)
            self.assertTrue(started["prompt"].endswith(prompt))
            self.assertIn("Do not delegate", started["prompt"][:-len(prompt)])
            self.assertEqual(started["cwd"], str(self.root))
        self.assertFalse(sentinel.exists())

    def test_model_effort_flags_and_requested_result_metadata(self):
        jobs = self.jobs()
        for job, effort in zip(jobs, ("ultra", "xhigh", "max")):
            job.update(model="model name; literal", effort=effort)
        completed = self.invoke(jobs)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        results = self.results(completed)
        for job, name, result in zip(jobs, ("codex", "claude", "agy"), results):
            args = self.started(name)["args"]
            self.assertEqual(args[args.index("--model") + 1], job["model"])
            if name == "codex":
                self.assertEqual(args[args.index("-c") + 1], 'model_reasoning_effort="ultra"')
            else:
                self.assertEqual(args[args.index("--effort") + 1], job["effort"])
            self.assertEqual(result["model"], job["model"])
            self.assertEqual(result["effort"], job["effort"])
        completed = self.invoke(self.jobs())
        self.assertEqual(completed.returncode, 0, completed.stderr)
        for name in ("codex", "claude", "agy"):
            args = self.started(name)["args"]
            self.assertNotIn("--model", args)
            self.assertNotIn("--effort", args)
            self.assertNotIn("-c", args)

    def test_invalid_manifest_starts_nothing(self):
        base = self.jobs()[0]
        invalid = [[], [base] * 2, self.jobs() + [base]]
        invalid += [[dict(base, **change)] for change in (
            {"surprise": True}, {"timeout_seconds": True}, {"timeout_seconds": 0},
            {"timeout_seconds": 3601}, {"timeout_seconds": float("nan")},
            {"context_only": True, "access": "edit"}, {"cwd": "relative"},
            {"prompt": " "}, {"access": "full"}, {"agent": "unknown"},
            {"model": ""}, {"model": "  "}, {"model": None}, {"model": "a\0b"},
            {"model": 1}, {"effort": ""}, {"effort": "unsupported"}, {"effort": None},
            {"effort": "high\0"}, {"agent": "claude", "effort": "ultra"},
            {"agent": "antigravity", "effort": "xhigh"})]
        for jobs in invalid:
            with self.subTest(jobs=jobs):
                completed = self.invoke(jobs)
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertFalse(list(self.root.glob("*.started")))
        self.manifest.write_text('{"jobs": [], "jobs": []}')
        completed = subprocess.run([sys.executable, str(RUNNER), str(self.manifest)],
                                   env=self.env, capture_output=True, text=True, timeout=5)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("duplicate", completed.stderr)

    def test_failed_responses_and_missing_binary_fail_closed(self):
        for prompt in ("json-error", "malformed", "unknown", "duplicate", "nonzero"):
            with self.subTest(prompt=prompt):
                completed = self.invoke(self.jobs(prompt))
                self.assertEqual(completed.returncode, 1)
                self.assertTrue(all(r["status"] == "failed" and r.get("error")
                                    for r in self.results(completed)))
        (self.bin / "codex").unlink()
        completed = self.invoke(self.jobs()[:1])
        self.assertEqual(completed.returncode, 2)
        self.assertIn("not installed", completed.stderr)
        self.assertEqual(completed.stdout, "")

    def test_review_edit_and_context_permissions(self):
        for access, expected in (("review", ("read-only", "plan", "plan")),
                                 ("edit", ("workspace-write", "acceptEdits", "accept-edits"))):
            completed = self.invoke([dict(job, access=access) for job in self.jobs()])
            self.assertEqual(completed.returncode, 0, completed.stderr)
            for name, mode in zip(("codex", "claude", "agy"), expected):
                self.assertIn(mode, self.started(name)["args"])
        completed = self.invoke([dict(job, context_only=True) for job in self.jobs()])
        self.assertEqual(completed.returncode, 0, completed.stderr)
        args = self.started("claude")["args"]
        self.assertEqual(args[args.index("--tools") + 1], "")
        self.assertIn("--strict-mcp-config", args)
        for name in ("codex", "claude", "agy"):
            self.assertIn("Use only the supplied context.", self.started(name)["prompt"])
            self.assertIn("Do not delegate", self.started(name)["prompt"])
            self.assertNotEqual(self.started(name)["cwd"], str(self.root))
            self.assertIn("cogitor-iso-", self.started(name)["cwd"])

    def test_reusable_api_hashes_validated_request_and_pre_cancel(self):
        runner = self.runner()
        jobs = self.jobs()[:1]
        self.manifest.write_text(json.dumps({"jobs": jobs}))
        validated = runner.load_jobs(self.manifest)
        expected = dict(jobs[0], access="review", context_only=False)
        self.assertEqual(validated, [expected])
        encoded = json.dumps(expected, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        self.assertEqual(runner.fingerprint(jobs[0]), hashlib.sha256(encoded).hexdigest())
        self.assertNotEqual(runner.fingerprint(jobs[0]), runner.fingerprint(dict(jobs[0], effort="high")))
        args, stdin = runner.command(validated[0])
        self.assertEqual(args[0], "codex")
        self.assertTrue(stdin.endswith(b"ok"))
        directory = self.root / "results"
        directory.mkdir(mode=0o700)
        cancelled = threading.Event()
        cancelled.set()
        with patch.dict(os.environ, self.env, clear=True):
            result = runner.execute_jobs(jobs, directory, cancelled)[0]
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["request_hash"], hashlib.sha256(encoded).hexdigest())
        self.assertFalse(list(self.root.glob("*.started")))

    def test_execute_jobs_rejects_unsafe_or_nonempty_directory(self):
        runner = self.runner()
        directory = self.root / "results"
        directory.mkdir(mode=0o755)
        with self.assertRaises(ValueError):
            runner.execute_jobs(self.jobs(), directory)
        directory.chmod(0o700)
        (directory / "keep").write_text("original")
        with self.assertRaises(ValueError):
            runner.execute_jobs(self.jobs(), directory)
        self.assertEqual((directory / "keep").read_text(), "original")
        self.assertFalse(list(self.root.glob("*.started")))

    def test_timeout_and_signals_clean_up_process_group(self):
        completed = self.invoke([dict(self.jobs("timeout")[0], timeout_seconds=.3)])
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(self.results(completed)[0]["status"], "timeout")
        time.sleep(1.2)
        self.assertFalse((self.root / "orphan-survived").exists())
        for signum, expected_code in ((signal.SIGINT, 130), (signal.SIGTERM, 143)):
            (self.root / "child.pid").unlink()
            self.manifest.write_text(json.dumps({"jobs": self.jobs("interrupt")[:1]}))
            process = subprocess.Popen([sys.executable, str(RUNNER), str(self.manifest)],
                                       env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 5
                while not (self.root / "child.pid").exists() and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertTrue((self.root / "child.pid").exists())
                process.send_signal(signum)
                stdout, stderr = process.communicate(timeout=5)
                self.assertEqual(process.returncode, expected_code, stderr)
                self.assertEqual(json.loads(stdout)["jobs"][0]["status"], "cancelled")
                time.sleep(1.2)
                self.assertFalse((self.root / "orphan-survived").exists())
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()

    def test_antigravity_argv_byte_ceiling(self):
        runner = self.runner()
        base = dict(agent="antigravity", cwd=str(self.root))
        with self.assertRaisesRegex(ValueError, "safe argv limit"):
            runner.validate_jobs([dict(base, prompt="a" * 100_001)])
        validated = runner.validate_jobs([dict(base, prompt="a" * 100_000)])
        self.assertEqual(len(validated[0]["prompt"]), 100_000)
        # Claude and Codex are not bound to 100k argv limit
        for agent in ("codex", "claude"):
            other = runner.validate_jobs([dict(agent=agent, cwd=str(self.root), prompt="a" * 150_000)])
            self.assertEqual(len(other[0]["prompt"]), 150_000)

    def test_tolerant_codex_event_parsing(self):
        runner = self.runner()
        log_file = self.root / "codex.stdout.log"
        lines = [
            "warning: non-json line to be skipped",
            json.dumps({"type": "thread.started", "thread_id": "thread-123"}),
            json.dumps({"type": "telemetry.ping", "timestamp": 123456789}),
            json.dumps({"type": "item.started", "item": {"id": "1"}}),
            json.dumps({"type": "item.completed", "item": {"type": "command_execution", "cmd": "pwd"}}),
            json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "Valid response."}}),
            json.dumps({"type": "item.updated", "extra": "data"}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 10}}),
        ]
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        parsed = runner.parse_response("codex", log_file)
        self.assertEqual(parsed["session_id"], "thread-123")
        self.assertEqual(parsed["response"], "Valid response.")
        self.assertEqual(parsed["usage"], {"input_tokens": 10})

        # Test failure if turn.failed or error
        for err_type in ("turn.failed", "error"):
            bad_lines = lines + [json.dumps({"type": err_type})]
            log_file.write_text("\n".join(bad_lines) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Codex reported " + err_type):
                runner.parse_response("codex", log_file)

        # Test failure if incomplete (no turn.completed)
        incomplete_lines = lines[:-1]
        log_file.write_text("\n".join(incomplete_lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "did not provide a completed turn"):
            runner.parse_response("codex", log_file)

    def test_max_output_bytes_exceeded(self):
        runner = self.runner()
        with patch.dict(os.environ, self.env, clear=True):
            with patch.object(runner, "MAX_OUTPUT_BYTES", 50):
                job = dict(agent="claude", cwd=str(self.root), prompt="ok", timeout_seconds=5)
                directory = self.root / "capped_results"
                directory.mkdir(mode=0o700)
                res = runner.run_job(job, directory, threading.Event())
                self.assertEqual(res["status"], "failed")
                self.assertIn("maximum allowed size", res["error"])


if __name__ == "__main__":
    unittest.main()
