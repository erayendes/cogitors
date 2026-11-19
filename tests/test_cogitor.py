"""Offline checks for the real round controller; only the model boundary is fake."""

import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "cogitors" / "scripts"


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
        # Most tests exercise rounds, not consent; approve scope right after init.
        self.raw_init = self.engine.init_run

        def init_approved(*args, **kwargs):
            directory = self.raw_init(*args, **kwargs)
            self.engine.approve_scope(directory)
            return directory
        approved = patch.object(self.engine, "init_run", side_effect=init_approved)
        approved.start()
        self.addCleanup(approved.stop)
        self.temp = tempfile.TemporaryDirectory(prefix="cogitor-check-")
        self.root = Path(self.temp.name)
        self.global_config = self.root / "global-config.json"
        homes = {name: self.root / ("." + name) for name in ("codex", "claude")}
        env = patch.dict(os.environ, HOME=str(self.root), CODEX_HOME=str(self.root / "codex-home"))
        env.start()
        self.addCleanup(env.stop)
        isolated = patch.multiple(self.engine, GLOBAL_CONFIG_PATH=self.global_config, CONFIG_DIR=self.root,
                                  DEFAULT_ACCOUNT_DIRS=homes)
        isolated.start()
        self.addCleanup(isolated.stop)
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
        self.assertEqual(default.parent, (self.root / "docs" / "cogitors").resolve())
        self.assertFalse(default.exists())
        self.one_round()
        self.assertEqual(default.stat().st_mode & 0o777, 0o700)

        private = self.engine.init_run(
            self.brief, "codex", self.root, run_dir=self.root / "private-run", private=True)
        self.assertIsNone(self.engine.status(private)["output_dir"])

        output_root = self.root / "project" / "docs" / "cogitors"
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
            run_dir=self.root / "delivery-run", output_dir=self.root / "docs" / "cogitors")
        output = Path(self.engine.status(self.run_dir)["output_dir"])
        advisor_files = {f"{agent}-{self.slug}.md" for agent in ("codex", "claude", "antigravity")} | {f"brief-{self.slug}.md"}
        for stage in range(1, 5):
            self.one_round()
            self.assertEqual({path.name for path in output.iterdir()}, advisor_files)
            for name in advisor_files:
                self.assertEqual((output / name).read_text(), (self.run_dir / name).read_text())
                if name != f"brief-{self.slug}.md":
                    self.assertIn("## Round %s" % stage, (output / name).read_text())
        final = self.root / "decision.json"
        final.write_text(json.dumps(dict(answer="Use 10.", agreement="All agree.",
                                         dissent="None.", uncertainties="Not benchmarked.")))
        result = self.engine.finish(self.run_dir, final)
        final_files = {f"decision-{self.slug}.md", f"decisions-{self.slug}.html", f"metrics-{self.slug}.json"}
        self.assertEqual({path.name for path in output.iterdir()},
                          advisor_files | final_files)
        self.assertEqual(Path(result["final"]), output / f"decision-{self.slug}.md")
        self.assertEqual((output / f"decision-{self.slug}.md").read_text(), (self.run_dir / f"decision-{self.slug}.md").read_text())
        self.assertTrue((self.run_dir / "round-1" / "jobs.json").is_file())
        self.assertTrue((self.run_dir / "brief.md").is_file())

    def test_export_json_publishes_structured_decision_only_on_request(self):
        with self.assertRaisesRegex(ValueError, "export_json"):
            self.engine.init_run(self.brief, "codex", self.root, run_dir=self.root / "private-json-run",
                                 private=True, export_json=True)
        self.run_dir = self.engine.init_run(
            self.brief, "codex", self.root, sources=[self.source], run_dir=self.root / "json-run",
            output_dir=self.root / "json-decisions", export_json=True)
        output = Path(self.engine.status(self.run_dir)["output_dir"])
        for _ in range(4):
            self.one_round()
        answer = dict(answer="Use 10.", agreement="All agree.", dissent="None.", uncertainties="Not benchmarked.")
        final = self.root / "decision.json"
        final.write_text(json.dumps(answer))
        self.engine.finish(self.run_dir, final)
        self.assertEqual(json.loads((output / f"decision-{self.slug}.json").read_text()), answer)

    def test_call_budget_blocks_dispatch_and_retry_before_any_model_call(self):
        with self.assertRaisesRegex(ValueError, "max_calls"):
            self.engine.init_run(self.brief, "codex", self.root, run_dir=self.root / "bad-budget", max_calls=0)
        self.run_dir = self.engine.init_run(self.brief, "codex", self.root, sources=[self.source],
                                            run_dir=self.root / "budget-run", max_calls=3)
        self.assertEqual(self.engine.status(self.run_dir)["scope"]["call_budget"], 3)
        self.fail_at = (1, "antigravity")
        self.one_round()
        self.assertEqual(self.engine.status(self.run_dir)["calls_spent"], 2)
        self.fail_at = None
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.extend_timeout(self.run_dir)  # one retry fits: 3 of 3
            self.assertEqual(self.engine.status(self.run_dir)["calls_spent"], 3)
            self.engine.record_host(self.run_dir, self.host)
            with self.assertRaisesRegex(ValueError, "call budget exhausted"):
                self.engine.dispatch_round(self.run_dir)
        self.assertEqual(len(self.calls), 2)
        self.assertFalse((self.run_dir / "round-2" / "dispatched").exists())

    def test_protocol_warnings_reach_the_chair_without_extra_calls(self):
        self.host.write_text("Stance: limit 10.\n\nproposal.md says limit is 10.")
        for _ in range(4):
            self.one_round()
        warnings = self.engine.status(self.run_dir)["protocol_warnings"]
        self.assertIn(dict(round=1, agent="claude", issue="missing Stance line"), warnings)
        self.assertIn(dict(round=3, agent="antigravity", issue="round 3 critique cites no snapshot file"), warnings)
        self.assertFalse([w for w in warnings if w["agent"] == "codex"])
        self.assertIn("Protocol warnings", (self.run_dir / "synthesis.md").read_text())
        self.assertEqual(len(self.calls), 4)

    def test_finish_marks_whether_each_evidence_quote_is_in_the_snapshot(self):
        for _ in range(4):
            self.one_round()
        final = self.root / "decision.json"
        final.write_text(json.dumps(dict(
            answer="Use 10.", agreement="All agree.", dissent="None.", uncertainties="Not benchmarked.",
            evidence=[dict(source="proposal.md", quote="limit   is 10", claim="Ten is the limit."),
                      dict(source="proposal.md", quote="limit is 1000"),
                      dict(source="missing.md", quote="limit is 10")])))
        self.engine.finish(self.run_dir, final)
        saved = json.loads((self.run_dir / "decision.json").read_text())
        self.assertEqual([e["matched"] for e in saved["evidence"]], [True, False, False])
        report = (self.run_dir / f"decision-{self.slug}.md").read_text()
        self.assertIn('Quote matched in `proposal.md`: "limit   is 10" — Ten is the limit.', report)
        self.assertIn("Quote NOT found in `missing.md`", report)
        final.write_text(json.dumps(dict(answer="a", agreement="b", dissent="c", uncertainties="d",
                                         evidence=[dict(source="proposal.md")])))
        with self.assertRaisesRegex(ValueError, "verbatim quote"):
            self.engine.validate_synthesis(json.loads(final.read_text()), self.engine.AGENTS)

    def test_metrics_summary_aggregates_local_sessions_and_keeps_unknown_usage(self):
        decisions = self.root / "metric-decisions"
        for number in (1, 2):
            folder = decisions / ("2026-run-%s" % number)
            folder.mkdir(parents=True)
            usage = {"input_tokens": 100, "output_tokens": 50} if number == 1 else None
            (folder / "metrics-run.json").write_text(json.dumps(dict(
                status="complete", calls_spent=8, total_duration_seconds=100 * number,
                rounds={"1": {"jobs": {"claude": dict(duration_seconds=10 * number, usage=usage),
                                       "codex": dict(duration_seconds=5, usage=None)}}})))
        summary = self.engine.metrics_summary(decisions)
        self.assertEqual(summary["sessions"], 2)
        self.assertEqual(summary["calls_spent"], 16)
        self.assertEqual(summary["avg_total_seconds"], 150)
        self.assertEqual(summary["avg_round_seconds"], {"1": 15})
        self.assertEqual(summary["agents"]["claude"], dict(avg_call_seconds=15, tokens=150, calls_without_usage=1))
        self.assertEqual(summary["agents"]["codex"]["tokens"], "unknown")
        self.assertEqual(self.engine.metrics_summary(self.root / "nowhere")["sessions"], 0)

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
        self.assertIn("## Round 1", (self.run_dir / f"claude-{self.slug}.md").read_text())
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
        (output / f"codex-{self.slug}.md").symlink_to(outside)
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
            history = (self.run_dir / f"{agent}-{self.slug}.md").read_text()
            for stage in range(1, 5):
                self.assertIn("## Round %s" % stage, history)
        final = self.root / "final.json"
        final.write_text(json.dumps(dict(answer="Use 10.", agreement="All three support 10.",
                                         dissent="None remaining.", uncertainties="Not benchmarked.")))
        status = self.engine.finish(self.run_dir, final)
        self.assertEqual(status["status"], "complete")
        self.assertIn("Use 10.", (self.run_dir / f"decision-{self.slug}.md").read_text())
        self.assertIn("3/3", (self.run_dir / f"decision-{self.slug}.md").read_text())
        self.assertIn("Host: session-contextual (unmetered by runner).", (self.run_dir / f"decision-{self.slug}.md").read_text())
        # Verify finish is idempotent when called again
        idempotent_status = self.engine.finish(self.run_dir, final)
        self.assertEqual(idempotent_status["status"], "complete")
        self.assertEqual(self.source.read_text(), "Evidence: limit is 10, not 100.")

    def test_host_must_lock_own_view_before_peer_consumption(self):
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.dispatch_round(self.run_dir)
        with self.assertRaisesRegex(ValueError, "host|chair|own"):
            self.engine.advance(self.run_dir)
        self.assertFalse((self.run_dir / f"claude-{self.slug}.md").exists())
        self.engine.record_host(self.run_dir, self.host)
        self.host.write_text("Try to rewrite my independent view after seeing a peer")
        with self.assertRaises((ValueError, FileExistsError)):
            self.engine.record_host(self.run_dir, self.host)
        self.engine.advance(self.run_dir)
        self.assertIn("My independent position", (self.run_dir / f"codex-{self.slug}.md").read_text())

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
        self.assertEqual(result["decision"], ["extend-timeout", "continue-partial", "stop"])
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
        self.assertIn("2/3", (self.run_dir / f"decision-{self.slug}.md").read_text())

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
        self.assertTrue((self.run_dir / f"codex-{self.slug}.md").exists())
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
        self.assertFalse((self.run_dir / f"decision-{self.slug}.md").exists())

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


    def test_doctor_command(self):
        with patch.object(self.engine.shutil, "which", return_value=None):
            doc = self.engine.doctor(cwd=self.root, as_json=True)
        self.assertIn(doc["status"], ("ready", "degraded", "blocked"))
        self.assertIn("agents", doc)
        for agent in ("codex", "claude", "antigravity"):
            self.assertIn(agent, doc["agents"])
            self.assertIn("status", doc["agents"][agent])

    def test_two_agent_council(self):
        run_2 = self.engine.init_run(self.brief, "codex", self.root,
                                     run_dir=self.root / "two-agent-run",
                                     agents=["codex", "claude"])
        status = self.engine.status(run_2)
        self.assertEqual(status["active"], ["codex", "claude"])
        first_jobs = json.loads((Path(run_2) / "round-1" / "jobs.json").read_text())["jobs"]
        self.assertEqual([j["agent"] for j in first_jobs], ["claude"])

        for stage in range(1, 5):
            self.host.write_text("R%s codex 2-agent view" % stage)
            self.engine.record_host(run_2, self.host)
            with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
                self.engine.dispatch_round(run_2)
            self.engine.advance(run_2)

        final = self.root / "two_agent_final.json"
        final.write_text(json.dumps(dict(answer="Approved 10.", agreement="Both agree.",
                                         dissent="None.", uncertainties="None.")))
        fin_status = self.engine.finish(run_2, final)
        self.assertEqual(fin_status["status"], "complete")
        final_md = (Path(run_2) / f"decision-{self.slug}.md").read_text()
        self.assertIn("Participation: 2/2 — complete", final_md)
        self.assertTrue((Path(run_2) / f"codex-{self.slug}.md").exists())
        self.assertTrue((Path(run_2) / f"claude-{self.slug}.md").exists())
        self.assertFalse((Path(run_2) / f"antigravity-{self.slug}.md").exists())

    def test_git_diff_and_staged_snapshot(self):
        git_dir = self.root / "git_repo"
        git_dir.mkdir()
        subprocess.run(["git", "init"], cwd=git_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@cogitor.org"], cwd=git_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Cogitor Test"], cwd=git_dir, check=True)
        test_file = git_dir / "code.py"
        test_file.write_text("x = 1\n")
        subprocess.run(["git", "add", "code.py"], cwd=git_dir, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=git_dir, check=True)

        test_file.write_text("x = 2\n")
        brief = self.root / "git_brief.md"
        brief.write_text("Review git changes.")

        run_git = self.engine.init_run(brief, "codex", git_dir,
                                       run_dir=self.root / "git-run", git_diff=True)
        _, state = self.engine.load_state(run_git)
        sources = state["sources"]
        self.assertEqual(len(sources), 1)
        self.assertTrue(sources[0]["path"].startswith("git:diff"))
        self.assertIn("+x = 2", sources[0]["text"])

    def test_cycle_command_executes_entire_round(self):
        for stage in range(1, 5):
            self.host.write_text("R%s codex cycle view" % stage)
            with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
                res = self.engine.cycle(self.run_dir, self.host)
            if stage < 4:
                self.assertEqual(res["round"], stage + 1)
            else:
                self.assertEqual(res["status"], "ready")
        final = self.root / "cycle_final.json"
        final.write_text(json.dumps(dict(answer="Cycle done.", agreement="All.",
                                         dissent="None.", uncertainties="None.")))
        fin = self.engine.finish(self.run_dir, final)
        self.assertEqual(fin["status"], "complete")

    def test_multilingual_turkish_detection_and_focused_debate(self):
        tr_brief = self.root / "tr_task.md"
        tr_brief.write_text("# Mimari Tasarım Önerisi İncelemesi\nBu mimari tasarımı inceleyin.")
        tr_run = self.engine.init_run(tr_brief, "codex", self.root,
                                      run_dir=self.root / "tr-run")
        _, state = self.engine.load_state(tr_run)
        self.assertEqual(state["language"], "tr")

        # In Round 3, prompt should contain focused debate guidance in Turkish
        state["round"] = 3
        prompt = json.loads(self.engine.prompt_for(state, "claude", tr_brief.read_text()))
        self.assertIn("Pozisyonlar ayrışıyorsa tartışmalı iddialara odaklanın", prompt["round_goal"])
        self.assertIn("Siz koordinatör değil", prompt["instructions"])

    def test_html_decision_viewer_generation_and_md_export(self):
        for stage in range(1, 5):
            self.host.write_text("R%s view" % stage)
            self.one_round()
        final = self.root / "html_test_final.json"
        final.write_text(json.dumps(dict(answer="HTML Answer.", agreement="HTML Agreement.",
                                         dissent="HTML Dissent.", uncertainties="HTML Uncertainties.")))
        fin = self.engine.finish(self.run_dir, final)
        html_file = Path(self.run_dir) / f"decisions-{self.slug}.html"
        self.assertTrue(html_file.is_file())
        html_text = html_file.read_text(encoding="utf-8")
        self.assertIn("Deliberation Stance Evolution Matrix", html_text)
        self.assertIn("Elder</span>", html_text)
        self.assertNotIn("(est)", html_text)
        self.assertIn("HTML Answer.", html_text)
        self.assertIn("prefers-color-scheme", html_text)
        self.assertNotIn("toggleTheme", html_text)

    def test_models_catalog_and_discovery(self):
        with patch.object(self.engine, "fetch_codex_models", return_value=None), \
                patch.object(self.engine, "fetch_antigravity_models", return_value=None):
            catalog = self.engine.get_available_models_catalog()
        self.assertEqual(catalog["codex"]["default"], "gpt-6.1-sol")
        self.assertEqual(catalog["claude"]["default"], "sonnet")
        self.assertEqual(catalog["antigravity"]["default"], "gemini-4-neon-high")
        self.assertEqual([m[0] for m in catalog["antigravity"]["models"]], ["gemini-4-neon-high", "gemini-3.8-flash-high"])
        self.assertIn("ultra", self.engine.effort_choices("codex"))
        self.assertNotIn("ultra", self.engine.effort_choices("claude"))
        for agent in ("codex", "claude", "antigravity"):
            self.assertEqual(set(self.engine.effort_choices(agent)), self.engine.runner.EFFORTS[agent])
        listed = json.dumps({"models": [dict(slug="b", visibility="list", priority=2),
                                        dict(slug="hidden", visibility="hide", priority=0),
                                        dict(slug="a", visibility="list", priority=1, description="best")]})
        with patch.object(self.engine.shutil, "which", return_value="/bin/codex"), \
                patch.object(self.engine.subprocess, "run",
                             return_value=subprocess.CompletedProcess([], 0, stdout=listed, stderr="")):
            self.assertEqual(self.engine.fetch_codex_models(), [("a", "best"), ("b", "b")])
        agy = "Fetching available models...\ngemini-x-high\tGemini X (High)\n"
        with patch.object(self.engine.shutil, "which", return_value="/bin/agy"), \
                patch.object(self.engine.subprocess, "run",
                             return_value=subprocess.CompletedProcess([], 0, stdout=agy, stderr="")):
            self.assertEqual(self.engine.fetch_antigravity_models(), [("gemini-x-high", "Gemini X (High)")])
        with patch.object(self.engine.shutil, "which", return_value=None):
            models_data = self.engine.models_cmd(as_json=True)
        self.assertIn("codex", models_data["agents"])
        self.assertIn("available_models", models_data["agents"]["codex"])

    def test_configure_and_default_model_loading(self):
        local_cfg = self.root / ".cogitors.json"
        self.assertFalse(local_cfg.exists())
        saved = self.engine.configure_cmd(codex_model="o3-mini", codex_effort="medium",
                                          claude_model="opus", local=True, cwd=self.root)
        self.assertTrue(local_cfg.is_file())
        self.assertEqual(saved["codex"]["model"], "o3-mini")
        self.assertEqual(saved["claude"]["model"], "opus")

        # Verify load_default_config loads it
        loaded = self.engine.load_default_config(cwd=self.root)
        self.assertEqual(loaded["codex"]["model"], "o3-mini")

        # Test init_run with use_defaults=True automatically loads configuration
        test_run = self.engine.init_run(self.brief, "antigravity", self.root,
                                        use_defaults=True, run_dir=self.root / "default-run")
        _, state = self.engine.load_state(test_run)
        self.assertEqual(state["options"]["codex"]["model"], "o3-mini")
        self.assertEqual(state["options"]["claude"]["model"], "opus")

    def test_session_header_banner_generation(self):
        stat = self.engine.status(self.run_dir)
        self.assertIn("banner", stat)
        self.assertIn("banner_md", stat)
        self.assertIn("THE COGITORS COUNCIL SESSION", stat["banner"])
        self.assertIn("### 🏛️ The Cogitors Council Session", stat["banner_md"])
        self.assertIn("Chair", stat["banner"])

        # Test Turkish banner
        tr_brief = self.root / "tr_banner.md"
        tr_brief.write_text("# Türkçe Oturum Başlığı\nBu bir Türkçe oturumdur.")
        tr_run = self.engine.init_run(tr_brief, "antigravity", self.root, run_dir=self.root / "tr-banner-run")
        tr_stat = self.engine.status(tr_run)
        self.assertIn("Konu", tr_stat["banner"])
        self.assertIn("Başkan", tr_stat["banner"])
        self.assertIn("Heyet & Modeller", tr_stat["banner"])

    def test_init_direct_model_flags_override(self):
        # Override via kwargs directly
        override_run = self.engine.init_run(self.brief, "antigravity", self.root,
                                            codex_model="o1", codex_effort="high",
                                            claude_model="haiku",
                                            run_dir=self.root / "override-run")
        _, state = self.engine.load_state(override_run)
        self.assertEqual(state["options"]["codex"]["model"], "o1")
        self.assertEqual(state["options"]["codex"]["effort"], "high")
        self.assertEqual(state["options"]["claude"]["model"], "haiku")

    def test_extend_timeout_retries_only_failed_advisor_and_keeps_full_panel(self):
        self.fail_at = (1, "antigravity")
        result = self.one_round()
        self.assertEqual(result["status"], "awaiting-partial-decision")
        self.assertIn("extend-timeout", result["decision"])
        self.assertIn("antigravity", result["failures"])

        # On retry, let antigravity succeed
        self.fail_at = None
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            retried = self.engine.extend_timeout(self.run_dir, add_seconds=120)
        self.assertEqual(retried["status"], "active")
        self.assertEqual(retried["round"], 2)
        self.assertEqual(len(retried["active"]), 3)
        self.assertNotIn("antigravity", retried["failures"])

    def test_extend_timeout_uses_fresh_retry_dir_reports_calls_and_caps_extensions(self):
        self.fail_at = (1, "antigravity")
        self.one_round()
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            first = self.engine.extend_timeout(self.run_dir, add_seconds=60)
        self.assertEqual(first["retry_calls"], 1)
        self.assertEqual(first["extensions_left"], self.engine.MAX_EXTENSIONS - 1)
        self.assertTrue((self.run_dir / "round-1" / "cli-retry-1").is_dir())

        # Fail again in round 2 so a second waiting state exists, then exhaust the cap.
        state = json.loads((self.run_dir / "state.json").read_text())
        state["status"], state["round"] = "awaiting-partial-decision", 1
        state["extensions"] = {"1": self.engine.MAX_EXTENSIONS}
        (self.run_dir / "state.json").write_text(json.dumps(state))
        (self.run_dir / "round-1" / "results.json").write_text(json.dumps(
            [{"agent": "antigravity", "status": "timeout"}]))
        with self.assertRaisesRegex(ValueError, "extension limit"):
            self.engine.extend_timeout(self.run_dir)

    def test_quota_snapshots_and_states(self):
        accounts = {"extra": dict(agent="codex", config_dir=str(self.root / "extra")),
                    "reviewer": dict(agent="claude", config_dir=str(self.root / "reviewer"))}
        routing = {"standard": {"claude": {"effort": "medium"}}}  # no codex entry on purpose
        self.global_config.write_text(json.dumps(dict(accounts=accounts, usage={"reviewer": "~/usage.json"}, routing=routing)))
        sessions = self.root / ".codex" / "sessions" / "2026"  # the default account, not CODEX_HOME
        sessions.mkdir(parents=True)
        now = 1800000000
        old = sessions / "rollout-old.jsonl"
        new = sessions / "rollout-new.jsonl"
        event = dict(payload=dict(rate_limits=dict(primary=dict(used_percent=100, window_minutes=300, resets_at=now + 10))))
        old.write_text(json.dumps(event))
        os.utime(old, (now - 50, now - 50))
        event["payload"]["rate_limits"]["primary"]["used_percent"] = 90
        event["payload"]["rate_limits"]["secondary"] = dict(used_percent=100, window_minutes=10080, resets_at=now)
        new.write_bytes(b"x" * 1100000 + b"\n" + old.read_bytes() + b"\n" + json.dumps(event).encode() +
                        b'\n{"rate_limits": null}\n{"rate_limits":\xff')
        os.utime(new, (now - 10, now - 10))
        snapshot = self.root / "usage.json"
        snapshot.write_text(json.dumps({"rate_limits": {"seven_day": {"used_percentage": 95, "resets_at": now + 20}}}))
        os.utime(snapshot, (now - 30, now - 30))
        args = ["cogitor.py", "quota", "--cwd", str(self.root)]
        with patch.object(self.engine.time, "time", return_value=now), \
                patch.object(self.engine.subprocess, "run", side_effect=AssertionError("quota must be offline")), \
                patch.object(sys, "argv", args + ["--json"]), patch("builtins.print") as output:
            self.assertEqual(self.engine.main(), 0)
            report = json.loads(output.call_args.args[0])
            with patch.object(sys, "argv", args):
                output.reset_mock()
                self.assertEqual(self.engine.main(), 0)
                self.assertEqual(output.call_count, 5)
        self.assertEqual(report["routing"], routing)
        by_lion = {(e["name"], e["pool"]): e for e in report["lions"]}
        self.assertEqual(len(by_lion), 7)
        codex = by_lion["codex", "account"]
        self.assertEqual((codex["source"], codex["age_seconds"], codex["state"]), ("codex-session", 10, "ok"))
        self.assertEqual(codex["five_hour"], dict(used_percent=90, resets_at=now + 10))
        claude = by_lion["reviewer", "account"]
        self.assertEqual((claude["source"], claude["age_seconds"], claude["state"]), ("statusline", 30, "low"))
        self.assertIsNone(claude["five_hour"])
        self.assertEqual(by_lion["extra", "account"]["state"], "unknown")  # never use another account's session
        self.assertEqual(by_lion["antigravity", "gemini"]["state"], "unknown")
        extra = self.root / "extra" / "sessions"
        extra.mkdir(parents=True)
        (extra / "rollout-extra.jsonl").write_bytes(old.read_bytes())
        plan = dict(mode="same", task="check", lions=[dict(name="extra")])
        with patch.object(self.engine.time, "time", return_value=now):
            with self.assertRaisesRegex(ValueError, "extra/account.*" + self.engine.quota_time(now + 10)):
                self.engine.plan_jobs(plan, "claude", self.root)
            plan["lions"] = [dict(name="codex")]
            self.assertEqual(self.engine.plan_jobs(plan, "claude", self.root)[0]["agent"], "codex")
            plan["lions"] = [dict(name="codex", tier="standard")]
            with self.assertRaisesRegex(ValueError, "tier standard has no codex entry"):
                self.engine.plan_jobs(plan, "claude", self.root)
        for used, reset, expected in ((0, now + 1, "ok"), (90, now + 1, "ok"), (90.1, now + 1, "low"),
                                      (100, now + 1, "exhausted"), (100, now, "unknown")):
            with self.subTest(used=used, reset=reset):
                window = dict(used_percent=used, resets_at=reset)
                entry = self.engine.quota_entry(dict(name="claude", agent="claude"), "account",
                                                (window, None, now, "statusline"), {}, now)
                self.assertEqual(entry["state"], expected)
        # An overrun still reads as exhausted, not as missing data.
        self.assertEqual(self.engine.quota_window({"w": {"used_percent": 104, "resets_at": 5}}, "w", "used_percent"),
                         dict(used_percent=100, resets_at=5))
        # Codex: windows by length, only the account-wide limit, the whole file, and older sessions as fallback.
        home = self.root / "codex-check"
        day = home / "sessions" / "2027"
        day.mkdir(parents=True)
        weekly = dict(used_percent=100, window_minutes=10080, resets_at=now + 99)
        account = dict(limit_id="codex", primary=weekly, secondary=dict(used_percent=5, window_minutes=300, resets_at=now + 9))
        other = dict(limit_id="codex_other", primary=dict(used_percent=0, window_minutes=300, resets_at=now + 9))
        older = day / "rollout-older.jsonl"
        unlabelled = dict(primary=dict(used_percent=0, window_minutes=300, resets_at=now + 9))
        older.write_text(json.dumps(dict(payload=dict(rate_limits=account))) + "\n" +
                         json.dumps(dict(payload=dict(rate_limits=other))) + "\n" +
                         json.dumps(dict(payload=dict(rate_limits=unlabelled))) + "\n" + "y" * 1100000 + "\n")
        # Written last but measured earlier: the latest reading wins, not the latest file.
        stale = day / "rollout-stale.jsonl"
        stale.write_text(json.dumps(dict(timestamp="2027-01-15T07:00:00Z", payload=dict(rate_limits=unlabelled))) + "\n")
        os.utime(stale, (now - 1, now - 1))
        os.utime(older, (now - 20, now - 20))
        newest = day / "rollout-newest.jsonl"
        newest.write_text(json.dumps(dict(type="session_meta")) + "\n")
        os.utime(newest, (now - 5, now - 5))
        five, seven, seen, source = self.engine.codex_snapshot(home)
        self.assertEqual((five["used_percent"], seven["used_percent"], seen, source), (5, 100, now - 20, "codex-session"))
        # An old-style bare {agent: options} config keeps its models beside the newer sections.
        self.assertEqual(self.engine.config_models({"codex": {"model": "m"}, "usage": {}}), {"codex": {"model": "m"}})
        # A tier may be an ordered fallback list of lions; quota shows each step's state in order.
        fallback = [dict(lion="extra", model="m1", effort="high"), dict(lion="codex", model="m2")]
        self.global_config.write_text(json.dumps(dict(accounts=accounts, routing=dict(deep=fallback))))
        with patch.object(self.engine.time, "time", return_value=now):
            report = self.engine.quota_report(self.root)
            self.assertEqual(report["fallbacks"]["deep"], [dict(fallback[0], state="exhausted"), dict(fallback[1], state="ok")])
            plan = dict(mode="same", task="t", lions=[dict(name="codex", tier="deep")])
            self.assertEqual(self.engine.plan_jobs(plan, "claude", self.root)[0]["model"], "m2")
            # --check hands only runner fields to the preflight, whatever plan_jobs adds.
            plan_file = self.root / "tier-plan.json"
            plan_file.write_text(json.dumps(plan))
            validate = lambda jobs: self.engine.runner.validate_jobs(jobs) and dict(ready=True)
            with patch.object(self.engine.runner, "preflight", side_effect=validate), \
                    patch.object(sys, "argv", ["cogitor.py", "voltron", "--elder", "claude", "--check", "--plan",
                                               str(plan_file), "--cwd", str(self.root)]), patch("builtins.print"):
                self.assertEqual(self.engine.main(), 0)
            plan["lions"] = [dict(name="reviewer", tier="deep")]
            with self.assertRaisesRegex(ValueError, "no entry for lion reviewer"):
                self.engine.plan_jobs(plan, "claude", self.root)
        many = dict(accounts, **{n: dict(agent="claude", config_dir=str(self.root / n)) for n in ("one", "two")})
        self.global_config.write_text(json.dumps(dict(accounts=many)))
        self.assertEqual(len(self.engine.plan_jobs(dict(mode="same", task="t", lions=[dict(name="reviewer")]),
                                                   "claude", self.root)), 1)  # the cap counts lions that run
        with self.assertRaisesRegex(ValueError, "at most 5"):
            self.engine.plan_jobs(dict(mode="same", task="t"), "claude", self.root)
        for bad in ([], [dict(lion="nobody")], [dict(lion="codex"), dict(lion="codex")], [dict(lion="codex", extra=1)],
                    [dict(lion=["codex"])]):
            self.global_config.write_text(json.dumps(dict(accounts=accounts, routing=dict(deep=bad))))
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.engine.quota_report(self.root)

    def test_readme_test_counts_match_reality(self):
        guide = (Path(__file__).resolve().parent.parent / ".github" / "CONTRIBUTING.md").read_text(encoding="utf-8")
        total = sum(1 for f in Path(__file__).parent.glob("test_*.py")
                    for line in f.read_text(encoding="utf-8").splitlines() if line.startswith("    def test_"))
        self.assertIn("%d testlik" % total, guide)
        self.assertIn("The %d-test suite" % total, guide)


    def test_dispatch_requires_single_scope_approval_and_status_reports_scope(self):
        run_dir = self.raw_init(self.brief, "codex", self.root, sources=[self.source],
                                run_dir=self.root / "scope-run")
        scope = self.engine.status(run_dir)["scope"]
        self.assertEqual(scope["providers"], ["claude", "antigravity"])
        self.assertEqual(scope["files"], 1)
        self.assertEqual(scope["max_calls"], 8)
        self.assertEqual(scope["max_calls_with_retries"], 8 * (1 + self.engine.MAX_EXTENSIONS))
        self.assertEqual(scope["peer_answers_sent_in_rounds"], [2, 3, 4])
        self.assertGreater(scope["bytes"], 0)
        self.assertEqual(scope["sources"], [dict(path=str(self.source.resolve()),
                                                 bytes=len(self.source.read_bytes()),
                                                 sha256=self.engine.digest(self.source.read_text()),
                                                 kind="source")])
        with self.assertRaisesRegex(ValueError, "scope not approved"):
            self.engine.dispatch_round(run_dir)
        self.assertFalse((run_dir / "round-1" / "dispatched").exists())
        self.assertTrue(self.engine.approve_scope(run_dir)["scope_approved"])


    def test_evidence_file_is_hashed_frozen_and_sent_from_round_one(self):
        report = self.root / "pytest.txt"
        report.write_text("FAILED test_limit: expected 10, got 100")
        run_dir = self.engine.init_run(self.brief, "codex", self.root, sources=[self.source],
                                       evidence=[report], run_dir=self.root / "evidence-run")
        state = json.loads((run_dir / "state.json").read_text())
        item = [s for s in state["sources"] if s.get("kind") == "evidence"][0]
        self.assertEqual(item["sha256"], self.engine.digest(report.read_text()))
        self.assertEqual(state["scope"]["evidence_files"], 1)
        jobs = json.loads((run_dir / "round-1" / "jobs.json").read_text())["jobs"]
        self.assertTrue(all("expected 10, got 100" in job["prompt"] for job in jobs))
        report.unlink()  # A temporary report may vanish; the stored text is the evidence.
        self.engine.check_snapshot(run_dir, state)


    def test_next_action_walks_the_round_and_never_retries_unknown_dispatch(self):
        run_dir = self.raw_init(self.brief, "codex", self.root, sources=[self.source],
                                run_dir=self.root / "next-run")
        action = lambda: self.engine.status(run_dir)["next_action"]
        self.assertEqual(action()["ask_user"], ["approve"])
        self.engine.approve_scope(run_dir)
        self.assertIn(" dispatch ", action()["command"])
        (run_dir / "round-1" / "dispatched").write_text("0")
        self.assertIn(" record ", action()["command"])  # the chair records while dispatch runs
        self.engine.record_host(run_dir, self.host)
        self.assertIsNone(action()["command"])  # outcome unknown: no command offered
        (run_dir / "round-1" / "dispatched").unlink()
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.dispatch_round(run_dir)
        self.assertIn(" advance ", action()["command"])

    def test_next_action_asks_user_on_partial_panel(self):
        self.fail_at = (1, "antigravity")
        result = self.one_round()
        self.assertIsNone(result["next_action"]["command"])
        self.assertEqual(result["next_action"]["ask_user"], ["extend-timeout", "continue-partial", "stop"])

    def test_round_three_prompt_targets_divergence_or_weakest_shared_assumption(self):
        for goals in (self.engine.ROUND_GOALS_EN, self.engine.ROUND_GOALS_TR):
            self.assertNotIn("do not re-debate", goals[3])
        self.assertIn("weakest assumption", self.engine.ROUND_GOALS_EN[3])
        self.assertIn("en zayıf", self.engine.ROUND_GOALS_TR[3])


    def test_structured_synthesis_renders_actions_and_per_cogitor_dissent_without_estimates(self):
        for stage in range(1, 5):
            self.host.write_text("Stance: codex holds limit 10 in round %s.\n\nDetails." % stage)
            self.one_round()
        final = self.root / "structured.json"
        final.write_text(json.dumps(dict(
            answer="Keep the limit.", agreement="All agree.", uncertainties="None measured.",
            dissent=[{"cogitor": "claude", "position": "Wants `100`.", "response": "Evidence says 10.",
                      "settle_by": "A load test at 100."}],
            actions=[{"priority": "P0", "text": "Fix the limit. Add a test."}], not_now=[{"item": "TUI", "reason": "Breaks zero dependencies."}],
            revisit={"date": "2026-12-01", "check": "No limit errors in the logs."})))
        self.engine.finish(self.run_dir, final)
        html_text = (Path(self.run_dir) / f"decisions-{self.slug}.html").read_text(encoding="utf-8")
        md_text = (Path(self.run_dir) / f"decision-{self.slug}.md").read_text(encoding="utf-8")
        self.assertIn("codex holds limit 10 in round 4.", html_text)  # explicit Stance line
        self.assertIn("<code>100</code>", html_text)
        self.assertIn("matrix-stance dissent", html_text)
        self.assertIn("prio-0", html_text)
        self.assertIn("<strong>TUI</strong> — Breaks zero dependencies.", html_text)
        self.assertNotIn("downloadMarkdown", html_text)
        self.assertIn("**claude:** Wants `100`.", md_text)
        self.assertIn("- **P0** Fix the limit. Add a test.", md_text)
        self.assertIn("*Settled by:* A load test at 100.", md_text)
        self.assertIn("**2026-12-01** — No limit errors in the logs.", md_text)
        self.assertIn("Settled by:</strong> A load test at 100.", html_text)
        self.assertIn("<strong>2026-12-01</strong> — No limit errors in the logs.", html_text)
        metrics = json.loads((Path(self.run_dir) / f"metrics-{self.slug}.json").read_text())
        self.assertEqual(metrics["revisit_date"], "2026-12-01")
        state = json.loads((Path(self.run_dir) / "state.json").read_text())
        self.assertIsInstance(state["metrics"]["rounds"]["1"]["jobs"]["codex"]["duration_seconds"], float)
        self.assertNotIn("tok", html_text.split("<tbody>")[1].split("</tbody>")[0])  # no usage reported, no tokens
        bad = self.root / "bad.json"
        bad.write_text(json.dumps(dict(answer="a", agreement="b", uncertainties="c",
                                       dissent=[{"cogitor": "nobody", "position": "x"}])))
        with self.assertRaisesRegex(ValueError, "dissent list items"):
            self.engine.validate_synthesis(json.loads(bad.read_text()), ["codex", "claude"])
        for revisit in ({"date": "2026-02-30", "check": "x"}, {"date": "20261201", "check": "x"},
                        {"date": "2026-12-01", "check": " "}, {"date": "2026-12-01"}, "2026-12-01"):
            with self.assertRaisesRegex(ValueError, "revisit needs"):
                self.engine.validate_synthesis(dict(answer="a", agreement="b", dissent="c", uncertainties="d",
                                                    revisit=revisit), ["codex"])

    def test_revisit_lists_only_sessions_whose_date_has_come(self):
        decisions = self.root / "revisit-decisions"
        for slug, date in (("later", "2026-12-01"), ("due", "2026-10-01"), ("today", "2026-10-28"), ("none", None)):
            folder = decisions / ("2026-%s" % slug)
            folder.mkdir(parents=True)
            (folder / ("metrics-%s.json" % slug)).write_text(json.dumps(dict(status="complete", revisit_date=date)))
        result = self.engine.revisit_due(decisions, today=self.engine.datetime.date(2026, 10, 28))
        self.assertEqual([d["slug"] for d in result["due"]], ["due", "today"])
        self.assertTrue(result["due"][0]["decision"].endswith("2026-due/decision-due.md"))
        self.assertEqual(self.engine.revisit_due(self.root / "nowhere")["due"], [])

    def test_voltron_runs_every_lion_but_the_elder_in_its_own_worktree(self):
        repo = self.root / "repo"
        repo.mkdir()
        git = lambda *args: subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t"]
                                           + list(args), check=True, capture_output=True, text=True).stdout
        git("init", "-q")
        (repo / "app.py").write_text("limit = 100\n")
        git("add", "-A")
        git("commit", "-qm", "init")
        (self.root / "work").mkdir()
        (repo / ".cogitors.json").write_text(json.dumps({"models": {"codex": {"model": "gpt-x"}},
                                                         "accounts": {"repo-owned": {"agent": "claude", "config_dir": "/"}}}))
        self.global_config.write_text(json.dumps({
            "accounts": {"codexwork": {"agent": "codex", "config_dir": str(self.root / "work"), "effort": "high"}}}))
        names = lambda elder: [w["name"] for w in self.engine.voltron_lions(elder, repo)]
        self.assertEqual(names("claude"), ["codex", "antigravity", "codexwork"])
        self.assertEqual(names("agy"), ["codex", "claude", "codexwork"])
        self.assertEqual(names("codexwork"), ["codex", "claude", "antigravity"])
        self.assertEqual([w["name"] for w in self.engine.voltron_lions("claude", repo, exclude=["agy"])],
                         ["codex", "codexwork"])
        with self.assertRaisesRegex(ValueError, "unknown lion"):
            self.engine.voltron_lions("gemini", repo)
        lions = self.engine.voltron_lions("claude", repo)
        self.assertEqual(lions[0]["config_dir"], None)  # built-in Codex ignores the host's CODEX_HOME
        self.assertEqual(lions[2], dict(name="codexwork", agent="codex", config_dir=str((self.root / "work").resolve()),
                                          effort="high", model="gpt-x"))
        # An account on the default Codex directory would run the built-in account twice.
        self.global_config.write_text(json.dumps({"accounts": {"twin": {"agent": "codex", "config_dir": "~/.codex"}}}))
        with self.assertRaisesRegex(ValueError, "same account directory"):
            self.engine.voltron_lions("claude", repo)
        self.global_config.write_text(json.dumps({
            "accounts": {"codexwork": {"agent": "codex", "config_dir": str(self.root / "work"), "effort": "high"}}}))

        def execute(jobs, directory, cancelled=None):
            for job in jobs:
                self.assertNotEqual(job["cwd"], str(repo.resolve()))
                if job["name"] == "codex":  # commits despite the prompt: the diff must still show it
                    (Path(job["cwd"]) / "app.py").write_text("limit = 10\r\n")
                    subprocess.run(["git", "-C", job["cwd"], "-c", "user.email=t@t", "-c", "user.name=t",
                                    "commit", "-qam", "fix"], check=True)
            return [dict(name=j["name"], agent=j["agent"], status="success", result_path="r") for j in jobs]
        task = self.root / "fix.md"
        task.write_text("Fix the limit.")
        with patch.object(self.engine.runner, "execute_jobs", side_effect=execute):
            summary = self.engine.voltron(task, "claude", repo, access="edit")
        jobs = {j["name"]: j for j in summary["jobs"]}
        self.assertEqual(sorted(jobs), ["antigravity", "codex", "codexwork"])
        self.assertTrue(jobs["codex"]["changed"])
        self.assertFalse(jobs["codexwork"]["changed"])
        self.assertIn(b"+limit = 10\r\n", Path(jobs["codex"]["diff_path"]).read_bytes())
        self.assertEqual((repo / "app.py").read_text(), "limit = 100\n")  # the checkout is untouched
        self.assertEqual(summary["mode"], "same")
        self.engine.voltron_clean(summary["run_dir"])
        self.assertFalse(Path(summary["run_dir"]).exists())
        self.assertEqual(len(git("worktree", "list").splitlines()), 1)
        with self.assertRaisesRegex(ValueError, "not a voltron run"):
            self.engine.voltron_clean(repo)
        # A subdirectory task keeps its subdirectory inside each worktree.
        (repo / "pkg").mkdir()
        (repo / "pkg" / "x.py").write_text("x = 1\n")
        git("add", "-A")
        git("commit", "-qm", "pkg")
        seen = []
        with patch.object(self.engine.runner, "execute_jobs",
                          side_effect=lambda jobs, d, cancelled=None: seen.extend(j["cwd"] for j in jobs) or
                          [dict(name=j["name"], agent=j["agent"], status="success") for j in jobs]):
            summary = self.engine.voltron(task, "claude", repo / "pkg", access="edit")
        self.assertTrue(all(c.endswith("/pkg") for c in seen))
        self.engine.voltron_clean(summary["run_dir"])
        with self.assertRaisesRegex(ValueError, "git repository"):
            self.engine.voltron(task, "claude", self.root, access="edit")

    def test_config_keeps_accounts_and_reports_a_damaged_project_file(self):
        config = dict(accounts={"w": {"agent": "codex", "config_dir": str(self.root / "extra")}},
                      usage={"claude": "~/usage.json"}, routing={"light": {"codex": {"model": "fast", "effort": "low"}}})
        self.global_config.write_text(json.dumps(config))
        self.assertEqual(self.engine.load_default_config(self.root), {})  # accounts are not model options
        self.engine.save_config({"codex": {"model": "m"}})
        saved = json.loads(self.global_config.read_text())
        self.assertEqual({k: saved[k] for k in config}, config)
        self.assertEqual(self.engine.load_default_config(self.root), {"codex": {"model": "m"}})
        self.global_config.write_text(json.dumps({"codex": {"model": "old"}}))  # old bare format
        self.assertEqual(self.engine.load_default_config(), {"codex": {"model": "old"}})
        (self.root / ".cogitors.json").write_text("{broken")
        with self.assertRaisesRegex(ValueError, "cannot read"):
            self.engine.load_default_config(self.root)
        (self.root / ".cogitors.json").write_text(json.dumps(dict(usage={"codex": "local"}, routing={"light": {}})))
        entry = dict(name="w", tier="light")
        plan = dict(mode="same", task="check", lions=[entry])
        self.global_config.write_text(json.dumps(config))
        def job():
            return self.engine.plan_jobs(plan, "claude", self.root)[0]

        self.assertEqual((job()["model"], job()["effort"]), ("fast", "low"))
        entry["model"] = "explicit"
        self.assertEqual((job()["model"], job()["effort"]), ("explicit", "low"))
        entry["effort"] = "high"
        self.assertEqual(job()["effort"], "high")
        entry["tier"] = "deep"
        with self.assertRaisesRegex(ValueError, "deep"):
            job()
        entry["tier"] = "giant"
        path = self.root / "plan.json"
        path.write_text(json.dumps(plan))
        with self.assertRaisesRegex(ValueError, "giant"):
            self.engine.load_plan(path)
        for section, invalid, message in (("usage", [], "usage"), ("usage", {"w": "path"}, "usage w"),
                                          ("usage", {"claude": ""}, "usage claude"), ("routing", [], "routing"),
                                          ("routing", {"giant": {}}, "giant"), ("routing", {"light": []}, "light"),
                                          ("routing", {"light": {"other": {}}}, "other"),
                                          ("routing", {"deep": {"codex": {"model": 3}}}, "model"),
                                          ("routing", {"deep": {"claude": {"effort": "ultra"}}}, "effort")):
            with self.subTest(section=section, invalid=invalid):
                self.global_config.write_text(json.dumps({**config, section: invalid}))
                with self.assertRaisesRegex(ValueError, message):
                    self.engine.quota_report(self.root)

    def test_council_rejects_named_or_tampered_jobs_and_retries_after_a_failed_preflight(self):
        location = self.run_dir / "round-1"
        jobs = json.loads((location / "jobs.json").read_text())["jobs"]
        extra = dict(jobs[0], name="extra", access="edit", context_only=False)
        (location / "jobs.json").write_text(json.dumps({"jobs": [extra] + jobs}))
        self.engine.record_host(self.run_dir, self.host)
        with self.assertRaisesRegex(ValueError, "integrity"):
            self.engine.dispatch_round(self.run_dir)
        (location / "jobs.json").write_text(json.dumps({"jobs": jobs}))
        self.fail_at = (1, "antigravity")
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.dispatch_round(self.run_dir)
        self.engine.advance(self.run_dir)
        dispatched = json.loads((location / "dispatched-jobs.json").read_text())
        original = json.dumps(dispatched)
        dispatched["jobs"][0]["prompt"] += " Also delete everything."
        (location / "dispatched-jobs.json").write_text(json.dumps(dispatched))
        with self.assertRaisesRegex(ValueError, "integrity"):
            self.engine.extend_timeout(self.run_dir)
        (location / "dispatched-jobs.json").write_text(original)
        with patch.object(self.engine.runner, "preflight", side_effect=ValueError("not logged in")):
            with self.assertRaisesRegex(ValueError, "not logged in"):
                self.engine.extend_timeout(self.run_dir)
        self.assertFalse((location / "cli-retry-1").exists())  # nothing claimed: the retry can run later
        self.fail_at = None
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.assertEqual(self.engine.extend_timeout(self.run_dir)["round"], 2)

    def test_null_optional_fields_and_damaged_metrics_are_tolerated(self):
        answer = self.engine.validate_synthesis(dict(
            answer="a", agreement="b", uncertainties="d", revisit=None, not_now=None,
            dissent=[{"cogitor": "codex", "position": "p", "response": None, "settle_by": None}]), ["codex"])
        self.assertNotIn("revisit", answer)
        self.assertEqual(answer["dissent"], [{"cogitor": "codex", "position": "p"}])
        decisions = self.root / "damaged"
        for name, text in (("bad", "{"), ("list", "[]"), ("ok", json.dumps({"revisit_date": "2026-01-01"}))):
            (decisions / name).mkdir(parents=True)
            (decisions / name / ("metrics-%s.json" % name)).write_text(text)
        result = self.engine.revisit_due(decisions)
        self.assertEqual([d["slug"] for d in result["due"]], ["ok"])
        self.assertEqual(len(result["skipped"]), 2)

    def test_git_diff_head_includes_staged_changes_and_interactive_needs_a_terminal(self):
        repo = self.root / "staged"
        repo.mkdir()
        run = lambda *a: subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t"] + list(a),
                                        check=True, capture_output=True)
        run("init", "-q")
        (repo / "a.txt").write_text("one\n")
        run("add", "-A")
        run("commit", "-qm", "init")
        (repo / "a.txt").write_text("two\n")
        run("add", "-A")  # staged only: the working tree equals the index
        directory = self.raw_init(self.brief, "codex", repo, git_diff="HEAD", run_dir=self.root / "staged-run")
        sources = json.loads((directory / "state.json").read_text())["sources"]
        self.assertTrue(any("+two" in s["text"] for s in sources))
        with patch.object(self.engine.sys.stdin, "isatty", return_value=False):
            with self.assertRaisesRegex(ValueError, "needs a terminal"):
                self.engine.pick_models_interactive()

    def test_followup_answers_land_in_the_report_without_changing_the_decision(self):
        self.run_dir = self.engine.init_run(self.brief, "codex", self.root, sources=[self.source],
                                            run_dir=self.root / "fu-run", output_dir=self.root / "out")
        for _ in range(4):
            self.one_round()
        final = self.root / "final.json"
        final.write_text(json.dumps(dict(answer="Use 10.", agreement="All agree.", dissent="None.",
                                         uncertainties="Not benchmarked.")))
        self.engine.finish(self.run_dir, final)
        folder = Path(self.engine.status(self.run_dir)["output_dir"])
        report = folder / f"decisions-{self.slug}.html"
        before = report.read_text()
        self.assertIn('id="dissent" data-ask=', before)
        self.assertIn(json.dumps(str(folder)), before)  # the copied command points at the folder the user reads
        self.assertEqual(self.engine.report_followups(report), [])
        answers = self.root / "answers.json"
        answers.write_text(json.dumps([
            dict(section="dissent", quote="None.", question="Why no dissent?", answer="All four rounds agreed </script>.",
                 effect="clarifies", basis="claude round 4"),
            dict(question="What if the limit is 1000?", answer="That is new information.", effect="challenges")]))
        result = self.engine.followup(folder, answers)
        self.assertEqual((result["added"], result["challenges"]), ([1, 2], [2]))
        records = self.engine.report_followups(report)
        self.assertEqual([(r["section"], r["id"]) for r in records], [("dissent", 1), ("general", 2)])
        self.assertIn("&lt;/script&gt;", records[0]["answer_html"])
        after = report.read_text()
        strip = lambda text: self.engine.FOLLOWUPS_BLOCK.sub("", text)
        self.assertEqual(strip(after), strip(before))  # only the follow-up block changed
        self.assertEqual(after.count("</script>"), before.count("</script>"))
        log = (folder / f"followup-{self.slug}.md").read_text()
        self.assertIn("**Question:** Why no dissent?", log)
        self.assertIn("Challenges the decision", log)
        answers.write_text(json.dumps(dict(question="Again?", answer="Yes.", effect="clarifies")))
        self.assertEqual(self.engine.followup(folder, answers)["total"], 3)
        # Re-rendering keeps the answers added to the exported copy.
        self.engine.export_html_cmd(self.run_dir)
        self.assertEqual(len(self.engine.report_followups(report)), 3)
        for bad in (dict(question="q", answer="a", effect="maybe"), dict(question=" ", answer="a", effect="clarifies"),
                    dict(question="q", answer="a", effect="clarifies", extra=1), []):
            answers.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                self.engine.followup(folder, answers)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.engine.followup(self.root, answers)

    def test_default_run_works_in_the_report_folder_and_removes_temp_when_finished(self):
        self.run_dir = self.raw_init(self.brief, "codex", self.root, sources=[self.source])
        self.engine.approve_scope(self.run_dir)
        folder = Path(self.engine.status(self.run_dir)["output_dir"])
        self.assertEqual(Path(self.run_dir), folder / "temp")
        self.assertEqual(folder.parent, (self.root / "docs" / "cogitors").resolve())
        self.assertEqual((folder / "temp" / ".gitignore").read_text(), "*\n")  # git never sees working files
        for _ in range(4):
            self.one_round()
        final = self.root / "final.json"
        final.write_text(json.dumps(dict(answer="Use 10.", agreement="All agree.", dissent="None.",
                                         uncertainties="Not benchmarked.")))
        result = self.engine.finish(self.run_dir, final)
        self.assertFalse((folder / "temp").exists())
        self.assertIsNone(result["run_dir"])
        self.assertEqual(result["final"], str(folder / f"decision-{self.slug}.md"))
        self.assertEqual(sorted(p.name for p in folder.iterdir()), sorted(
            [f"brief-{self.slug}.md", f"decision-{self.slug}.md", f"decisions-{self.slug}.html",
             f"metrics-{self.slug}.json"] + [f"{a}-{self.slug}.md" for a in self.engine.AGENTS]))

    def test_voltron_plan_splits_parts_from_the_uncommitted_working_tree(self):
        repo = self.root / "parts"
        repo.mkdir()
        git = lambda *args: subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t"]
                                           + list(args), check=True, capture_output=True, text=True).stdout
        git("init", "-q")
        (repo / "api").mkdir()
        (repo / "ui").mkdir()
        (repo / "api" / "a.py").write_text("a = 1\n")
        (repo / "ui" / "b.py").write_text("b = 1\n")
        git("add", "-A")
        git("commit", "-qm", "init")
        (repo / "types.py").write_text("Limit = int\n")  # the Elder's uncommitted shared scaffold
        status_before = git("status", "--porcelain")
        plan = self.root / "plan.json"
        plan.write_text(json.dumps(dict(mode="parts", task="Build the payment flow.", lions=[
            dict(name="codex", task="Write the API.", model="gpt-x", effort="high", owns=["api"]),
            dict(name="agy", task="Write the UI.", owns=["ui"])])))
        seen = {}

        def execute(jobs, directory, cancelled=None):
            for job in jobs:
                seen[job["name"]] = job
                worktree = Path(job["cwd"])
                self.assertEqual((worktree / "types.py").read_text(), "Limit = int\n")
                (worktree / ("api" if job["name"] == "codex" else "ui") / "x.py").write_text("x = 1\n")
                if job["name"] == "antigravity":
                    (worktree / "types.py").write_text("Limit = str\n")  # outside its part
            return [dict(name=j["name"], agent=j["agent"], status="success") for j in jobs]
        with patch.object(self.engine.runner, "execute_jobs", side_effect=execute):
            summary = self.engine.voltron(None, "claude", repo, access="edit", plan_path=plan)
        self.assertFalse(any("quota" in j for j in summary["jobs"]))
        self.assertEqual(summary["mode"], "parts")
        self.assertEqual(sorted(seen), ["antigravity", "codex"])  # only the plan's lions run
        self.assertEqual((seen["codex"]["model"], seen["codex"]["effort"]), ("gpt-x", "high"))
        self.assertIn("Your part:\nWrite the API.", seen["codex"]["prompt"])
        self.assertIn("Build the payment flow.", seen["codex"]["prompt"])
        self.assertIn("Change only these paths: api.", seen["codex"]["prompt"])
        jobs = {j["name"]: j for j in summary["jobs"]}
        self.assertEqual(jobs["codex"]["outside_owns"], [])
        self.assertEqual(jobs["antigravity"]["outside_owns"], ["types.py"])
        diff = Path(jobs["codex"]["diff_path"]).read_text()
        self.assertIn("api/x.py", diff)
        self.assertNotIn("types.py", diff)  # the scaffold is in the base, not in a lion's diff
        self.assertEqual(git("status", "--porcelain"), status_before)  # the user's checkout is untouched
        self.engine.voltron_clean(summary["run_dir"])
        for bad in (dict(mode="parts", lions=[dict(name="codex")]),
                    dict(mode="same", task="t", lions=[dict(name="codex", task="mine")]),
                    dict(mode="same", lions=[dict(name="codex")]),
                    dict(mode="parts", task="t", lions=[dict(name="codex", task="x", owns=["../out"])]),
                    dict(mode="both", lions=[dict(name="codex")])):
            plan.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                self.engine.load_plan(plan)
        plan.write_text(json.dumps(dict(mode="same", task="t", lions=[dict(name="claude")])))
        with self.assertRaisesRegex(ValueError, "not available"):  # the Elder is never a lion
            self.engine.voltron(None, "claude", repo, plan_path=plan)
        plan.write_text(json.dumps(dict(mode="same", task="t", lions=[dict(name="codex"), dict(name="agy", model="claude-x")])))
        error = "CLI exited with code 3: Individual quota reached. Resets in 17h"
        now = 1800000000
        # now is 2027-01-15 08:00 UTC
        for text, delay in (("Resets in 2h 30m", 9000), ("try again in 45 minutes", 2700), ("rate limited", 3600),
                            ("Please retry in 2.517s", 3), ("usage limit reached|%d" % (now + 14400), 14400),
                            ("resets at 1969-12-31T23:59:59Z", 3600), ("resets at 9999-12-31T23:59:59-05:00", 3600),
                            ("resets at 2027-01-15T09:00:00.123456789", 3601), ("resets 3pm (UTC)", 7 * 3600),
                            ("Try again at 7:30 am (UTC)", 23.5 * 3600), ("resets 3pm (Mars/Base)", 3600),
                            ("Resets at 3:00 p.m. (UTC)", 7 * 3600), ("Resets at 2027-01-15T12:00:00.", 4 * 3600),
                            ("Resets at 2027-01-15T13:00:00+0300", 2 * 3600), ("Retry-After: 120", 120),
                            ("retry in a moment; usage limit resets in 2h", 7200)):
            with self.subTest(text=text):
                self.assertEqual(self.engine.quota_reset(text, now), now + delay)
        self.assertLessEqual(self.engine.quota_reset("", self.engine.MAX_RESET - 10), self.engine.MAX_RESET)
        # Only a stated reset over a minute away, or a quota phrase with none, counts; a short or bare throttle does not.
        for text, quota in (("429 Too Many Requests. Retry in 59.9s", False), ("Retry in 60s", False),
                            ("429 retry in 0s", False), ("rate_limit_exceeded: retry in 500ms", False),
                            ("429 Too Many Requests. Please retry after 30 seconds", False), ("429 Too Many Requests", False),
                            ("Individual quota reached. Resets in 17h", True), ("RESOURCE_EXHAUSTED", True)):
            with self.subTest(text=text):
                self.assertEqual(self.engine.is_quota_failure("CLI exited with code 1: " + text, now), quota)
        # A clock time with no zone is local, and tomorrow keeps tomorrow's offset across a DST change.
        import zoneinfo
        new_york = zoneinfo.ZoneInfo("America/New_York")
        self.addCleanup(time.tzset)  # runs after the TZ patch below is undone
        with patch.dict(os.environ, TZ="America/New_York"):
            time.tzset()
            evening = datetime.datetime(2026, 10, 31, 22, 0, tzinfo=new_york).timestamp()
            self.assertEqual(self.engine.quota_reset("Try again at 3:14 PM", evening),
                             datetime.datetime(2026, 11, 1, 15, 14, tzinfo=new_york).timestamp())
        for text, quota in (("5-hour limit reached ∙ resets 3pm", True), ("Weekly limit reached", True),
                            ("You've hit your limit · resets 3pm", True), ("Error: 429 Too Many Requests", True),
                            ("You exceeded your current quota", True), ("unknown flag --quota-mode", False),
                            ("Disk quota exceeded", False), ("exceeded the limit on open files", False),
                            ("Request too large: exceeded the limit of 32MB", False),
                            ("Payload too large: you have exceeded your limit of 32MB", False),
                            ("open files: reached your limit of 1024 descriptors", False), ("limit reached|1800014400", True),
                            ("You've hit your 5-hour limit", True), ("you have exceeded your monthly quota", True)):
            with self.subTest(text=text):
                self.assertEqual(bool(self.engine.QUOTA_ERROR.search("CLI exited with code 1: " + text)), quota)
        with patch.object(self.engine.time, "time", return_value=now), \
                patch.object(self.engine.runner, "execute_jobs", side_effect=lambda jobs, d, cancelled=None: [
                    dict(name=j["name"], agent=j["agent"], status="timeout" if j["name"] == "codex" else "failed",
                         error=error) for j in jobs]):
            summary = self.engine.voltron(None, "claude", repo, plan_path=plan)
        self.assertEqual({j["name"]: j.get("quota", False) for j in summary["jobs"]}, {"codex": False, "antigravity": True})
        # Each run logs one line per lion: settings and outcome, never the prompt, answer or error text.
        run_log = self.global_config.with_name("runs.jsonl")
        runs = [json.loads(line) for line in run_log.read_text().splitlines()][-2:]  # earlier runs logged too
        self.assertEqual({(r["lion"], r["status"], r.get("quota", False), r["usage"], r["mode"]) for r in runs},
                         {("codex", "timeout", False, "unknown", "same"), ("antigravity", "failed", True, "unknown", "same")})
        self.assertTrue(all(set(r) <= {"time", "mode", "lion", "agent", "model", "effort", "tier", "status",
                                       "duration_seconds", "usage", "quota"} for r in runs))
        self.assertNotIn("Individual", run_log.read_text())
        self.assertEqual(run_log.stat().st_mode & 0o777, 0o600)
        until = now + 17 * 3600
        ledger = self.global_config.with_name("quota.json")
        self.assertEqual(ledger.stat().st_mode & 0o777, 0o600)
        self.assertEqual(json.loads(ledger.read_text()), dict(schema="cogitor.quota.v1", cooldowns={
            "antigravity/claude": dict(until=until, reason="quota reached", seen=now)}))  # never the full message
        with patch.object(self.engine.time, "time", return_value=now), patch.object(self.engine.runner, "preflight") as check:
            reset = self.engine.quota_time(until)
            with self.assertRaisesRegex(ValueError, "antigravity/claude.*" + reset):
                self.engine.voltron(None, "claude", repo, plan_path=plan)
            with patch.object(sys, "argv", ["cogitor.py", "voltron", "--elder", "claude", "--check", "--plan", str(plan),
                                            "--cwd", str(repo)]), patch("builtins.print") as output:
                self.assertEqual(self.engine.main(), 2)
                self.assertIn(reset, output.call_args.args[0])
            check.assert_not_called()
            # Without a plan, "every lion" means every lion with room: an exhausted one is skipped and named.
            planless = dict(mode="same", task="t")
            self.assertEqual([j["name"] for j in self.engine.plan_jobs(planless, "claude", repo)], ["codex"])
            self.assertEqual(planless["skipped"], ["antigravity/claude"])
            states = {e["pool"]: e for e in self.engine.quota_report(repo)["lions"] if e["agent"] == "antigravity"}
            self.assertEqual(states["claude"]["source"], "cooldown")
            self.assertEqual(states["gemini"]["state"], "unknown")
        with patch.object(self.engine.time, "time", return_value=until):
            self.assertEqual(len(self.engine.plan_jobs(self.engine.load_plan(plan), "claude", repo)), 2)
            self.assertTrue(all(e["cooldown_until"] is None for e in self.engine.quota_report(repo)["lions"]))
            self.engine.record_cooldown(dict(name="codex", agent="codex", model="example"), "quota exceeded " + "x" * 200)
            records = json.loads(ledger.read_text())["cooldowns"]
            self.assertEqual(records["codex/account"]["until"], until + 3600)
            self.assertEqual(records["codex/account"]["reason"], "quota exceeded")
            self.assertNotIn("antigravity/claude", records)  # expired blocks are pruned on write
            # A shorter block never overwrites a longer one for the same pool.
            self.engine.record_cooldown(dict(name="codex", agent="codex"), "quota exceeded. Resets in 5m")
            self.assertEqual(json.loads(ledger.read_text())["cooldowns"]["codex/account"]["until"], until + 3600)
            # An Antigravity lion without a model may land in any pool, so every pool's block applies.
            self.engine.record_cooldown(dict(name="antigravity", agent="antigravity", model="gemini-x"), "RESOURCE_EXHAUSTED")
            unset = dict(mode="same", task="t", lions=[dict(name="agy")])
            with self.assertRaisesRegex(ValueError, "antigravity/gemini"):
                self.engine.plan_jobs(unset, "claude", repo)
            # A failure without a model may have used any pool, so it blocks all three.
            self.engine.record_cooldown(dict(name="antigravity", agent="antigravity"), "RESOURCE_EXHAUSTED")
            self.assertTrue({"antigravity/claude", "antigravity/gemini", "antigravity/other"} <=
                            set(json.loads(ledger.read_text())["cooldowns"]))
            self.assertEqual(self.global_config.with_name("quota.lock").stat().st_mode & 0o777, 0o600)
        self.engine.voltron_clean(summary["run_dir"])
        # A throttle that clears within a minute is a plain failure: no reassignment, no cooldown.
        throttle = "CLI exited with code 1: 429 Too Many Requests. Please retry in 2s"
        before = ledger.read_text()
        with patch.object(self.engine.time, "time", return_value=until + 7200), \
                patch.object(self.engine.runner, "execute_jobs", side_effect=lambda jobs, d, cancelled=None: [
                    dict(name=j["name"], agent=j["agent"], status="failed", error=throttle) for j in jobs]):
            throttled = self.engine.voltron(None, "claude", repo, plan_path=plan)
        self.assertFalse(any(j.get("quota") for j in throttled["jobs"]))
        self.assertEqual(self.engine.runs_summary()["antigravity/claude-x"],
                         dict(runs=2, avg_seconds=None, success_rate=0.0, quota_rate=0.5))
        with patch.object(sys, "argv", ["cogitor.py", "metrics", "--dir", str(self.root / "none")]), \
                patch("builtins.print") as output:
            self.assertEqual(self.engine.main(), 0)
        self.assertIn("antigravity/claude-x", json.loads(output.call_args.args[0])["lions"])
        # Only numeric top-level counters reach disk; nested text from a provider never does.
        self.assertEqual(self.engine.usage_counters({"input_tokens": 4, "geo": "global",
                                                     "diagnostic": {"prompt": "secret"}}), {"input_tokens": 4})
        self.assertEqual(self.engine.usage_counters(None), "unknown")
        self.assertEqual(ledger.read_text(), before)
        self.engine.voltron_clean(throttled["run_dir"])
        # Partial success exits 0; only a run where no lion succeeded is a failure.
        plan.write_text(json.dumps(dict(mode="same", task="t", lions=[dict(name="codex"), dict(name="agy")])))
        for statuses, code in ((("success", "failed"), 0), (("failed", "timeout"), 1)):
            outcome = dict(jobs=[dict(name=n, status=st) for n, st in zip(("codex", "antigravity"), statuses)])
            with patch.object(self.engine, "voltron", return_value=outcome), \
                    patch.object(sys, "argv", ["cogitor.py", "voltron", "--elder", "claude", "--plan", str(plan)]), \
                    patch("builtins.print"):
                self.assertEqual(self.engine.main(), code)


if __name__ == "__main__":
    unittest.main()

