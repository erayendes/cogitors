"""Offline checks for the real round controller; only the model boundary is fake."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "cogitor" / "scripts"


class CogitorCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert (SCRIPTS / "cogitor.py").is_file(), "Cogitor round controller is not implemented"
        sys.path.insert(0, str(SCRIPTS))
        spec = importlib.util.spec_from_file_location("cogitor", SCRIPTS / "cogitor.py")
        cls.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.engine)

    def setUp(self):
        preflight = patch.object(self.engine.runner, "preflight")
        preflight.start()
        self.addCleanup(preflight.stop)
        self.temp = tempfile.TemporaryDirectory(prefix="cogitor-check-")
        self.root = Path(self.temp.name)
        self.brief = self.root / "task.md"
        self.brief.write_text("Review the same complete proposal. Do not edit it.")
        self.slug = "review-the-same-complete-proposal"
        self.source = self.root / "proposal.md"
        self.source.write_text("Evidence: limit is 10, not 100.")
        self.host = self.root / "host.md"
        self.host.write_text("My independent position: limit 10, with evidence.")
        self.calls = []
        self.fail_at = None
        self.run_dir = self.engine.init_run(self.brief, "codex", self.root,
                                            sources=[self.source], run_dir=self.root / "run")

    def tearDown(self):
        self.temp.cleanup()

    def execute(self, jobs, directory, cancelled=None):
        self.calls.append(jobs)
        results = []
        for job in jobs:
            payload = json.loads(job["prompt"])
            stage, agent = payload["round"], job["agent"]
            failed = self.fail_at == (stage, agent) or self.fail_at == (stage, "all")
            text = "R%s %s: final correction limit 10" % (stage, agent)
            result = dict(agent=agent, status="failed" if failed else "success",
                          response=None if failed else text, session_id="session-%s" % agent,
                          request_hash=self.engine.runner.fingerprint(job), usage=None,
                          error="unavailable" if failed else None)
            results.append(result)
        return results

    def one_round(self):
        self.engine.record_host(self.run_dir, self.host)
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.dispatch_round(self.run_dir)
        return self.engine.advance(self.run_dir)

    def test_output_defaults_to_project_docs_with_an_explicit_private_opt_out(self):
        default = Path(self.engine.status(self.run_dir)["output_dir"])
        self.assertEqual(default.parent, (self.root / "docs" / "cogitors-decisions").resolve())
        self.assertFalse(default.exists())
        self.one_round()
        self.assertEqual(default.stat().st_mode & 0o777, 0o700)

        private = self.engine.init_run(
            self.brief, "codex", self.root, run_dir=self.root / "private-run", private=True)
        self.assertIsNone(self.engine.status(private)["output_dir"])

        output_root = self.root / "project" / "docs" / "cogitors-decisions"
        output_root.mkdir(parents=True)
        existing = output_root / "notes.md"
        existing.write_text("Keep this existing project file.")
        outputs = []
        for number in (1, 2):
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "cogitor.py"), "init", str(self.brief),
                 "--chair", "codex", "--cwd", str(self.root), "--run-dir",
                 str(self.root / ("export-run-%s" % number)), "--output-dir", str(output_root),
                 "--slug", "run-%s" % number],
                capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = Path(json.loads(result.stdout)["output_dir"])
            self.assertEqual(output.parent, output_root.resolve())
            self.assertFalse(output.exists())
            outputs.append(output)
        self.assertNotEqual(outputs[0], outputs[1])
        self.assertEqual(existing.read_text(), "Keep this existing project file.")

    def test_slug_generation_and_custom_slug(self):
        brief = self.root / "turkish_task.md"
        brief.write_text("# Cogitor Müzakere ve Tekli Skill Ekosistemi Kapsamlı Sentez Raporu\nDetaylar...")
        run_dir = self.engine.init_run(brief, "codex", self.root, run_dir=self.root / "slug-run")
        output = Path(self.engine.status(run_dir)["output_dir"])
        self.assertTrue(output.name.endswith("-cogitor-muzakere-ve-tekli-skill"))

        custom_run = self.engine.init_run(brief, "codex", self.root,
                                          run_dir=self.root / "custom-slug-run", slug="ozel-baslik")
        custom_output = Path(self.engine.status(custom_run)["output_dir"])
        self.assertTrue(custom_output.name.endswith("-ozel-baslik"))

    def test_only_advisor_histories_and_final_decision_are_exported(self):
        self.run_dir = self.engine.init_run(
            self.brief, "codex", self.root, sources=[self.source],
            run_dir=self.root / "delivery-run", output_dir=self.root / "docs" / "cogitors-decisions")
        output = Path(self.engine.status(self.run_dir)["output_dir"])
        advisor_files = {f"cogitor-{agent}-{self.slug}.md" for agent in ("codex", "claude", "antigravity")}
        for stage in range(1, 5):
            self.one_round()
            self.assertEqual({path.name for path in output.iterdir()}, advisor_files)
            for name in advisor_files:
                self.assertEqual((output / name).read_text(), (self.run_dir / name).read_text())
                self.assertIn("## Round %s" % stage, (output / name).read_text())
        final = self.root / "decision.json"
        final.write_text(json.dumps(dict(answer="Use 10.", agreement="All agree.",
                                         dissent="None.", uncertainties="Not benchmarked.")))
        result = self.engine.finish(self.run_dir, final)
        final_files = {f"cogitor-final-{self.slug}.md", f"cogitor-final-{self.slug}.json"}
        self.assertEqual({path.name for path in output.iterdir()},
                          advisor_files | final_files)
        self.assertEqual(Path(result["final"]), output / f"cogitor-final-{self.slug}.md")
        self.assertEqual(json.loads((output / f"cogitor-final-{self.slug}.json").read_text()),
                         dict(answer="Use 10.", agreement="All agree.",
                              dissent="None.", uncertainties="Not benchmarked."))
        self.assertEqual((output / f"cogitor-final-{self.slug}.md").read_text(), (self.run_dir / f"cogitor-final-{self.slug}.md").read_text())
        self.assertTrue((self.run_dir / "round-1" / "jobs.json").is_file())
        self.assertTrue((self.run_dir / "brief.md").is_file())

    def test_export_failure_is_visible_and_keeps_completed_round_without_retry(self):
        self.run_dir = self.engine.init_run(
            self.brief, "codex", self.root, run_dir=self.root / "failed-delivery-run",
            output_dir=self.root / "decisions")
        output = Path(self.engine.status(self.run_dir)["output_dir"])
        output.write_text("Existing file must survive the export failure.")
        result = self.one_round()
        self.assertEqual(result["round"], 2)
        self.assertIn("export", result["export_error"])
        self.assertEqual(len(self.calls), 1)
        self.assertIn("## Round 1", (self.run_dir / f"cogitor-claude-{self.slug}.md").read_text())
        self.assertEqual(output.read_text(), "Existing file must survive the export failure.")
        self.assertFalse((self.run_dir / "round-1" / "advanced").exists())

    def test_export_rejects_symlink_without_overwriting_unrelated_file(self):
        self.run_dir = self.engine.init_run(
            self.brief, "codex", self.root, run_dir=self.root / "linked-output-run",
            output_dir=self.root / "decisions")
        output = Path(self.engine.status(self.run_dir)["output_dir"])
        output.mkdir(mode=0o700, parents=True, exist_ok=True)
        outside = self.root / "keep.md"
        outside.write_text("Keep this unrelated file.")
        (output / f"cogitor-codex-{self.slug}.md").symlink_to(outside)
        result = self.one_round()
        self.assertEqual(outside.read_text(), "Keep this unrelated file.")
        self.assertEqual(result["round"], 2)
        self.assertIn("export", result["export_error"])

    def test_five_stages_and_latest_views_reach_synthesis(self):
        first = json.loads((self.run_dir / "round-1" / "jobs.json").read_text())
        self.assertEqual([j["agent"] for j in first["jobs"]], ["claude", "antigravity"])
        for job in first["jobs"]:
            self.assertEqual(json.loads(job["prompt"])["previous_rounds"], {})
        for stage in range(1, 5):
            self.host.write_text("R%s codex: keep limit 10; response to objections" % stage)
            self.one_round()
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(sum(map(len, self.calls)), 8)
        synth = (self.run_dir / "synthesis.md").read_text()
        self.assertIn("R4 claude: final correction limit 10", synth)
        self.assertIn("R4 antigravity: final correction limit 10", synth)
        self.assertIn("R4 codex: keep limit 10", synth)
        self.assertIn("R3 claude", synth)
        self.assertIn("R1 codex", synth)
        for agent in ("codex", "claude", "antigravity"):
            history = (self.run_dir / f"cogitor-{agent}-{self.slug}.md").read_text()
            for stage in range(1, 5):
                self.assertIn("## Round %s" % stage, history)
        final = self.root / "final.json"
        final.write_text(json.dumps(dict(answer="Use 10.", agreement="All three support 10.",
                                         dissent="None remaining.", uncertainties="Not benchmarked.")))
        status = self.engine.finish(self.run_dir, final)
        self.assertEqual(status["status"], "complete")
        self.assertIn("Use 10.", (self.run_dir / f"cogitor-final-{self.slug}.md").read_text())
        self.assertIn("3/3", (self.run_dir / f"cogitor-final-{self.slug}.md").read_text())
        self.assertIn("Host: session-contextual (unmetered by runner).", (self.run_dir / f"cogitor-final-{self.slug}.md").read_text())
        # Verify finish is idempotent when called again
        idempotent_status = self.engine.finish(self.run_dir, final)
        self.assertEqual(idempotent_status["status"], "complete")
        self.assertEqual(self.source.read_text(), "Evidence: limit is 10, not 100.")

    def test_host_must_lock_own_view_before_peer_consumption(self):
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.dispatch_round(self.run_dir)
        with self.assertRaisesRegex(ValueError, "host|chair|own"):
            self.engine.advance(self.run_dir)
        self.assertFalse((self.run_dir / f"cogitor-claude-{self.slug}.md").exists())
        self.engine.record_host(self.run_dir, self.host)
        self.host.write_text("Try to rewrite my independent view after seeing a peer")
        with self.assertRaises((ValueError, FileExistsError)):
            self.engine.record_host(self.run_dir, self.host)
        self.engine.advance(self.run_dir)
        self.assertIn("My independent position", (self.run_dir / f"cogitor-codex-{self.slug}.md").read_text())

    def test_no_repeat_dispatch_or_fifth_round_model_call(self):
        self.one_round()
        self.engine.record_host(self.run_dir, self.host)
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.dispatch_round(self.run_dir)
            with self.assertRaises((ValueError, FileExistsError)):
                self.engine.dispatch_round(self.run_dir)
        self.engine.advance(self.run_dir)
        self.one_round()
        self.one_round()
        with self.assertRaises(ValueError):
            self.engine.dispatch_round(self.run_dir)
        self.assertEqual(len(self.calls), 4)

    def test_partial_panel_waits_for_user_choice_and_does_not_retry_failed_advisor(self):
        self.fail_at = (1, "antigravity")
        result = self.one_round()
        self.assertEqual(result["status"], "awaiting-partial-decision")
        self.assertEqual(result["decision"], ["continue-partial", "stop"])
        self.assertEqual(result["completed_rounds"], 1)
        self.assertFalse((self.run_dir / "round-2").exists())

        result = self.engine.continue_partial(self.run_dir)
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["round"], 2)
        for _ in range(3):
            self.one_round()
        self.assertEqual([len(calls) for calls in self.calls], [2, 1, 1, 1])
        synth = (self.run_dir / "synthesis.md").read_text()
        self.assertIn("antigravity", synth)
        self.assertIn("failed", synth)
        final = self.root / "partial.json"
        final.write_text(json.dumps(dict(answer="Provisional 10.", agreement="Two participants support 10.",
                                         dissent="No final view from Antigravity.", uncertainties="Partial panel.")))
        result = self.engine.finish(self.run_dir, final)
        self.assertEqual(result["status"], "partial")
        self.assertIn("2/3", (self.run_dir / f"cogitor-final-{self.slug}.md").read_text())

    def test_round_four_failure_requires_choice_before_synthesis(self):
        for _ in range(3):
            self.one_round()
        self.fail_at = (4, "claude")
        result = self.one_round()
        self.assertEqual(result["status"], "awaiting-partial-decision")
        self.assertEqual(result["round"], 4)
        self.assertFalse((self.run_dir / "synthesis.md").exists())

        result = self.engine.continue_partial(self.run_dir)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["round"], 5)
        self.assertTrue((self.run_dir / "synthesis.md").is_file())

    def test_fewer_than_two_positions_blocks_and_keeps_artifacts(self):
        self.fail_at = (1, "all")
        state = self.one_round()
        self.assertEqual(state["status"], "blocked")
        self.assertTrue((self.run_dir / f"cogitor-codex-{self.slug}.md").exists())
        self.assertFalse((self.run_dir / "round-2").exists())
        with self.assertRaises(ValueError):
            self.engine.dispatch_round(self.run_dir)

    def test_changed_sources_block_next_dispatch(self):
        self.one_round()
        self.source.write_text("Now the source is different")
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            with self.assertRaisesRegex(ValueError, "source|snapshot|changed"):
                self.engine.dispatch_round(self.run_dir)
        self.assertEqual(len(self.calls), 1)

    def test_wrong_result_provenance_is_rejected(self):
        self.engine.record_host(self.run_dir, self.host)
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.dispatch_round(self.run_dir)
        path = self.run_dir / "round-1" / "results.json"
        data = json.loads(path.read_text())
        data[0]["request_hash"] = "another-job"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "provenance|hash|match"):
            self.engine.advance(self.run_dir)

    def test_invalid_settings_and_final_do_not_silently_fallback(self):
        for options in ({"gpt": {}}, {"claude": {"extra": True}},
                        {"claude": {"effort": "invalid"}}):
            with self.assertRaises(ValueError):
                self.engine.init_run(self.brief, "codex", self.root, options=options,
                                     run_dir=self.root / "invalid")
            self.assertFalse((self.root / "invalid").exists())
        for _ in range(4):
            self.one_round()
        final = self.root / "final.json"
        final.write_text('{"answer": "Only an answer without agreement or dissent"}')
        with self.assertRaises(ValueError):
            self.engine.finish(self.run_dir, final)
        self.assertFalse((self.run_dir / f"cogitor-final-{self.slug}.md").exists())

    def test_deadline_prevents_dispatch_and_caps_remaining_time(self):
        state = json.loads((self.run_dir / "state.json").read_text())
        with patch.object(self.engine.time, "time", return_value=state["deadline"] + 1):
            with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
                with self.assertRaisesRegex(ValueError, "deadline"):
                    self.engine.dispatch_round(self.run_dir)
        self.assertEqual(self.calls, [])
        self.assertFalse((self.run_dir / "round-1" / "dispatched").exists())
        with patch.object(self.engine.time, "time", return_value=state["deadline"] - .5):
            with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
                self.engine.dispatch_round(self.run_dir)
        self.assertTrue(all(job["timeout_seconds"] == .5 for job in self.calls[0]))
        self.engine.record_host(self.run_dir, self.host)
        self.engine.advance(self.run_dir)

    def test_failed_preflight_does_not_claim_or_dispatch_the_round(self):
        with patch.object(self.engine.runner, "preflight", side_effect=ValueError("preflight failed")):
            with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
                with self.assertRaisesRegex(ValueError, "preflight failed"):
                    self.engine.dispatch_round(self.run_dir)
        self.assertFalse((self.run_dir / "round-1" / "dispatched").exists())
        self.assertEqual(self.calls, [])

    def test_altered_job_cannot_expand_permissions_or_change_model(self):
        path = self.run_dir / "round-1" / "jobs.json"
        data = json.loads(path.read_text())
        data["jobs"][0]["access"] = "edit"
        path.write_text(json.dumps(data))
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            with self.assertRaisesRegex(ValueError, "changed|integrity|match|invalid"):
                self.engine.dispatch_round(self.run_dir)
        self.assertEqual(self.calls, [])

    def test_actual_cli_five_round_flow_with_fake_executables(self):
        # Exercise the real controller, adapter, subprocess transport, and artifact readers.
        bindir = self.root / "bin"
        bindir.mkdir()
        fake = r'''
import json, os, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
agent = "antigravity" if name == "agy" else "claude"
if name == "claude" and sys.argv[1:] == ["auth", "status"]:
    print(json.dumps({"loggedIn": True}))
    sys.exit(0)
prompt = sys.argv[sys.argv.index("-p") + 1] if name == "agy" else sys.stdin.read()
payload = json.loads(prompt.rsplit("\n\n", 1)[-1])
stage = payload["round"]
previous = payload["previous_rounds"]
assert payload["advisor"] == agent
if stage == 1:
    assert previous == {}
else:
    assert set(previous[str(stage - 1)]) == {"codex", "claude", "antigravity"}
if stage == 4:
    assert set(previous) == {"3"}
pathlib.Path(os.environ["COGITOR_CHECK_DIR"], agent + "-" + str(stage)).write_text(prompt)
answer = "Fresh R%s %s position with evidence" % (stage, agent)
if name == "agy":
    data = dict(status="SUCCESS", response=answer, conversation_id="a-" + str(stage))
else:
    data = dict(subtype="success", is_error=False, result=answer, session_id="c-" + str(stage))
print(json.dumps(data))
'''
        for name in ("claude", "agy"):
            executable = bindir / name
            executable.write_text("#!" + sys.executable + "\n" + fake)
            executable.chmod(0o700)
        env = dict(os.environ, PATH=str(bindir), COGITOR_CHECK_DIR=str(self.root),
                   PYTHONDONTWRITEBYTECODE="1")

        def invoke(*args):
            bootstrap = ("import sys; sys.path.insert(0, sys.argv.pop(1)); import run, cogitor; "
                         "from unittest.mock import patch; "
                         "patch.object(run, 'probe_antigravity').start(); sys.exit(cogitor.main())")
            result = subprocess.run([sys.executable, "-c", bootstrap, str(SCRIPTS), *map(str, args)],
                                    env=env, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            return json.loads(result.stdout)

        for stage in range(1, 5):
            self.assertTrue(invoke("check", self.run_dir)["ready"])
            # Dispatch itself exposes metadata only. Host work can run in parallel in a real host.
            result = invoke("dispatch", self.run_dir)
            self.assertNotIn("response", json.dumps(result))
            self.host.write_text("Fresh R%s codex position with evidence" % stage)
            invoke("record", self.run_dir, "--file", self.host)
            invoke("advance", self.run_dir)
        synth = (self.run_dir / "synthesis.md").read_text()
        self.assertIn("Fresh R4 claude position", synth)
        self.assertIn("Fresh R4 antigravity position", synth)
        self.assertEqual(len(list(self.root.glob("claude-[1-4]"))), 4)
        self.assertEqual(len(list(self.root.glob("antigravity-[1-4]"))), 4)
        final = self.root / "cli-final.json"
        final.write_text(json.dumps(dict(answer="Use 10.", agreement="Shared evidence for 10.",
                                         dissent="None.", uncertainties="Offline simulation only.")))
        self.assertEqual(invoke("finish", self.run_dir, "--file", final)["status"], "complete")


if __name__ == "__main__":
    unittest.main()
