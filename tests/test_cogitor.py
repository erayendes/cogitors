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
        final_files = {f"decision-{self.slug}.md", f"decisions-{self.slug}.html"}
        self.assertEqual({path.name for path in output.iterdir()},
                          advisor_files | final_files)
        self.assertEqual(Path(result["final"]), output / f"decision-{self.slug}.md")
        self.assertEqual((output / f"decision-{self.slug}.md").read_text(), (self.run_dir / f"decision-{self.slug}.md").read_text())
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
        catalog = self.engine.get_available_models_catalog()
        self.assertIn("codex", catalog)
        self.assertIn("claude", catalog)
        self.assertIn("antigravity", catalog)
        self.assertEqual(catalog["codex"]["default"], "o3")
        self.assertEqual(catalog["claude"]["default"], "sonnet")
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

    def test_effort_choices_follow_runner_including_ultra(self):
        self.assertIn("ultra", self.engine.effort_choices("codex"))
        self.assertNotIn("ultra", self.engine.effort_choices("claude"))
        for agent in ("codex", "claude", "antigravity"):
            self.assertEqual(set(self.engine.effort_choices(agent)), self.engine.runner.EFFORTS[agent])

    def test_readme_test_counts_match_reality(self):
        root = Path(__file__).resolve().parent.parent
        readme = (root / "README.md").read_text(encoding="utf-8")
        readme_tr = (root / "docs" / "README.tr.md").read_text(encoding="utf-8")
        total = sum(1 for f in Path(__file__).parent.glob("test_*.py")
                    for line in f.read_text(encoding="utf-8").splitlines() if line.startswith("    def test_"))
        self.assertIn("%d testlik" % total, readme_tr)
        self.assertIn("The %d-test suite" % total, readme)


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
        self.assertIsNone(action()["command"])  # outcome unknown: no command offered
        (run_dir / "round-1" / "dispatched").unlink()
        with patch.object(self.engine.runner, "execute_jobs", side_effect=self.execute):
            self.engine.dispatch_round(run_dir)
        self.assertIn(" record ", action()["command"])
        self.engine.record_host(run_dir, self.host)
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
            dissent=[{"cogitor": "claude", "position": "Wants `100`.", "response": "Evidence says 10."}],
            actions=[{"priority": "P0", "text": "Fix the limit. Add a test."}], not_now=[{"item": "TUI", "reason": "Breaks zero dependencies."}])))
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
        state = json.loads((Path(self.run_dir) / "state.json").read_text())
        self.assertIsInstance(state["metrics"]["rounds"]["1"]["jobs"]["codex"]["duration_seconds"], float)
        self.assertNotIn("tok", html_text.split("<tbody>")[1].split("</tbody>")[0])  # no usage reported, no tokens
        bad = self.root / "bad.json"
        bad.write_text(json.dumps(dict(answer="a", agreement="b", uncertainties="c",
                                       dissent=[{"cogitor": "nobody", "position": "x"}])))
        with self.assertRaisesRegex(ValueError, "dissent list items"):
            self.engine.validate_synthesis(json.loads(bad.read_text()), ["codex", "claude"])


if __name__ == "__main__":
    unittest.main()

