# Host-assisted workflow

The Cogitors is a skill, not a new model service. The host supplies its own four advisor contributions and final synthesis. The script calls only the other CLIs, at most once per advisor per round (eight calls for three participants), plus up to two user-approved timeout retries per round; `status.scope.max_calls_with_retries` is the ceiling. Model-internal tool turns are not covered by this invocation count.

Use the actual installed script path. A shell that supports background jobs lets the host work while the other advisors run. `check`, `status`, `init`, `approve`, `record`, `advance` and `finish` never call a model; `dispatch`, `cycle` and `extend-timeout` do. Run round jobs only through those three: they enforce the no-repeat gate.

## 1. Initialize

Write the full assignment to a UTF-8 brief through the host's file tool. Include purpose, exact scope, allowed changes, expected deliverable and evidence requirements. The brief and selected source files form the shared snapshot. External advisors run in an empty temporary directory and see only the brief, `--source`, `--evidence-file` and `--git-diff`/`--git-staged` text, so pass every file they need with a repeated `--source`. `--git-diff [REF]` snapshots `git diff REF` (default `HEAD`, which includes staged changes); `--git-staged` snapshots only staged changes. All advisors receive the complete task.

For empirical grounding, run tests, lint or static analysis yourself, save the output to a file and pass it with repeated `--evidence-file`. Every advisor sees it from round 1. Its text is hashed and frozen at `init`, so a temporary report may be deleted afterwards. Cogitors never runs commands itself. Evidence counts toward the 200000-character shared limit and toward `status.scope`; it is not redacted, so trim secrets, tokens and unrelated logs before passing it.

```sh
python3 /actual/cogitors/scripts/cogitor.py init /path/brief.md \
  --chair codex --cwd /path/project --source /path/project/proposal.md
```

Pass `--chair-model <model>` with the host's own model as it knows it; the report marks it self-reported, since the runner cannot verify it. Advisors begin every response with a `Stance:` line (`Duruş:` for a Turkish brief), which the report's stance matrix shows; start your own record with the same line.

The returned `run_dir` is a fresh private temporary directory. `--run-dir /new/directory` selects a persistent destination but refuses any existing directory. Paths are examples, not personal defaults. Immediately tell the user the returned `output_dir`.

By default, `init` targets a unique session subfolder named `<timestamp>-<slug>` under `CWD/docs/cogitors-decisions/`. Optional `--slug my-topic` specifies the slug; otherwise it is automatically extracted from the first heading or line of the brief. The folder is created on the first completed round, containing only `brief-<slug>.md`, `codex-<slug>.md`, `claude-<slug>.md`, `antigravity-<slug>.md` and, when finished, `decision-<slug>.md`, `decisions-<slug>.html` and `metrics-<slug>.json` (durations, calls and any reported usage; no model text). `metrics [--dir DIR]` summarizes those files across finished sessions in `DIR` (default `CWD/docs/cogitors-decisions`): average session and round time, per-agent call time, and tokens per agent or `unknown` when a provider reported none. Pass `--export-json` to also export the structured synthesis as `decision-<slug>.json`; it cannot combine with `--private`. Use `--output-dir` for another destination or `--private` when the user requests no exported files. These are model outputs, not automatically redacted public documents; review before committing. Jobs, raw logs, credentials, and state are never exported. An export failure retains private results and reports the problem; do not repeat model calls to repair file delivery.

Defaults: 180 seconds per external invocation and a 1800-second run deadline. `--timeout` (up to 3600) and `--total-timeout` honor an explicitly agreed time budget. The run deadline counts wall-clock time from `init`, including the approval wait and the chair's own work; set it generously when that work is long. It prevents starting remote work after expiry and caps remaining dispatch time; it cannot terminate the current host's own thinking. Once dispatch reports `run deadline exhausted`, the run cannot continue: report it and ask before a new paid run. The host also respects the user's overall deadline.

### Models

- `models` lists the installed CLIs, their login status and the models they offer.
- `configure --codex-model M --codex-effort E --claude-model M ... [--local]` saves defaults to `~/.cogitors/config.json` (or the project's `.cogitors.json`); `configure --show` prints them. Later `init` calls inherit them.
- `configure -i` and `init -i` are menus that need a real terminal: ask the user to run them, since in an agent shell they stop with an error.
- `init --codex-model`, `--codex-effort`, `--claude-model`, `--claude-effort`, `--antigravity-model` and `--antigravity-effort` override the saved defaults for one run. `--options FILE` replaces the saved defaults instead of merging with them.
- A model or effort the user selects for the host's own provider cannot be applied by the runner and is dropped; tell the user and pass the host's actual model as `--chair-model`.
- `banner RUN_DIR [--markdown]` reprints the session header that `init` returns as `banner` and `banner_md`.

## 2. Repeat advisor rounds 1–4

Before the first dispatch, show the user `status.scope` from `init`: providers, file count, each file's path, size and hash (`sources`), bytes/characters, rounds, that peer answers are sent in rounds 2-4, `max_calls` and `max_calls_with_retries`. When the user sets a cost limit, pass `--max-calls N`: it becomes `scope.call_budget`, every dispatch and timeout retry counts against it the moment it is claimed (an unknown outcome is still spent), and `status.calls_spent` reports the total. A call that would exceed it is refused before any model runs. Ask once for explicit consent to that whole scope, then run `approve RUN_DIR`. `dispatch` refuses until approved; do not approve on the user's behalf.

First run `check RUN_DIR` in the context intended for dispatch. Follow [execution](execution.md) for narrowly approved host permissions if it fails. Each dispatch checks again before claiming its marker; failed checks spend no model tokens. An approved check does not grant future dispatch commands permission automatically.

1. Read `chair_prompt` from `status`. Start `dispatch RUN_DIR` as a host-managed background job, with the approved execution scope when required. Its stdout contains status metadata only, not peer answers.
2. Independently produce the chair's advisor contribution in a scratch file. In the first round, do not read any other advisor's output. In later rounds, use only the completed previous-round material provided in the prompt; do not read same-round peers early.
3. Run `record RUN_DIR --file /path/host-answer.md` while dispatch is still running; `status.next_action` offers it then. Recording is exclusive: a submitted view cannot be rewritten after seeing a peer.
4. Wait for the dispatch job to finish. On cancellation, stop. On a participant failure, inspect the status without retrying it.
5. Run `advance RUN_DIR`. It requires the host record, validates result provenance and source hashes, writes the advisor histories, and prepares the next round. Read only these normalized outputs when needed, not entire CLI logs.

Tell the user when each round starts and completes. When an advisor fails and at least two participants remain, `advance` returns `awaiting-partial-decision`: report the round as paused, name the failed advisor and wait for the user's choice. When fewer than two remain, status is `blocked`: no retry is offered; report the failures and stop.

1. **Extend Timeout & Retry (`extend-timeout`) — Recommended for Timeouts:**
   ```sh
   python3 /actual/cogitors/scripts/cogitor.py extend-timeout /path/run --add 180
   ```
   Retries only the failed advisors (at least 30 seconds are added), then advances by itself: do not run `advance` afterwards. The longer timeout applies to all later rounds. Allowed twice per round; each retry counts against `--max-calls`.

2. **Continue with Remaining Panel (`continue-partial`):**
   ```sh
   python3 /actual/cogitors/scripts/cogitor.py continue-partial /path/run
   ```
   Drops the failed advisor and continues the deliberation with the surviving participants.

3. **Stop:** not a command; run nothing further. All generated artifacts remain.

```sh
python3 /actual/cogitors/scripts/cogitor.py dispatch /path/run
python3 /actual/cogitors/scripts/cogitor.py record /path/run --file /path/host-answer.md
python3 /actual/cogitors/scripts/cogitor.py advance /path/run
```

The shell snippet shows command forms; start `dispatch` with the host's background mechanism so the chair can work concurrently. Alternatively, write the host answer first and run `cycle RUN_DIR --file /path/host-answer.md` to record, dispatch and advance in sequence, with dispatch in the foreground. If it fails after recording, continue with `dispatch` and `advance`, not `cycle`.

After the user chooses `continue-partial`, two survivors continue through the same rounds with explicit partial coverage. A dropped advisor's earlier view remains evidence, never a final vote. Fewer than two survivors blocks the run. A source change also stops progression: do not mix versions or silently start the whole paid run again. Preserve artifacts and report the reason.

`status.next_action` names the single safe next step for the current state: a runnable `command`, or `command: null` with `ask_user` choices or a note. After a crash it offers no command while a `dispatched` marker has no results. `dispatched` markers deliberately survive crashes. A crash after starting a remote request cannot establish whether that request spent tokens; do not delete the marker or retry automatically. Ask before a new paid run. Partial local writes may require inspection rather than automatic recovery.

## 3. Synthesize once

After round 4, status is `ready`, round is `5`, and `synthesis.md` contains the original task, source snapshot, all four rounds, final views and failures, plus any `protocol_warnings` (a missing `Stance:` line, or a round 3 critique that names no snapshot file). These are format checks only: they never trigger a retry, and a flagged answer still counts. The chair reads it and writes JSON. `answer`, `agreement` and `uncertainties` are nonempty strings. `dissent` is a string, or one item per dissenting participant with the majority's reply and, optionally, `settle_by`: the evidence that would settle it. `actions`, `not_now`, `evidence` and `revisit` are optional. `revisit` is `{date: YYYY-MM-DD, check}`, where `check` says what would show the answer was right or wrong; `python3 /actual/cogitors/scripts/cogitor.py revisit [--dir DIR]` lists finished sessions whose date has come. Each `evidence` item is `{source, quote, claim}` with a quote copied verbatim from a snapshot file; `finish` marks it matched or not found. A match only proves the quote is in the snapshot, not that the claim is right; keep actions out of `answer`, since the report lists them separately:

```json
{
  "answer": "The supported recommendation or deliverable.",
  "agreement": "Which conclusions are shared, by whom; explicitly say when none are shared.",
  "dissent": [{"cogitor": "antigravity", "position": "The minority position.", "response": "Why the others disagree.", "settle_by": "The evidence that would settle it."}],
  "uncertainties": "Unverified assumptions, missing checks and limits.",
  "actions": [{"priority": "P0", "text": "Title. One-sentence detail."}],
  "not_now": [{"item": "Deferred item", "reason": "Why it waits."}],
  "revisit": {"date": "2027-01-15", "check": "What would show the answer was right or wrong."}
}
```

```sh
python3 /actual/cogitors/scripts/cogitor.py finish /path/run --file /path/final.json
```

`decision-<slug>.md` adds actual participation coverage, a comparison matrix, and timing metrics. A standalone `decisions-<slug>.html` report is also exported. Present one coherent output in the user's language, retaining the required distinctions, and provide the absolute `final` path returned by `finish`.

## Artifacts and exits

- `state.json`: settings, shared evidence, round results, raw provider usage when available.
- `brief-<slug>.md`, `codex-<slug>.md`, `claude-<slug>.md`, `antigravity-<slug>.md`: session brief and separate named histories, including failed/missing rounds.
- `round-N/`: chair prompt, immutable chair submission, prepared `jobs.json`, deadline-capped `dispatched-jobs.json`, dispatch marker, normalized results and private CLI logs. Prepared requests are hashed in state; changed jobs are rejected before execution.
- `synthesis.md`, `decision.json`, `decision-<slug>.md`, `decisions-<slug>.html`, `metrics-<slug>.json`: synthesis input, final decision outputs and timing metrics.
- `calls.log`: one line per claimed model call, the source of `status.calls_spent`.
- `output_dir` in status: optional project delivery folder; `export_error` reports delivery failures without discarding private results.

Exit 0 means the operation succeeded; 1 reports failed dispatch jobs, a paused or blocked panel, an export error or a partial final result; 2 is an invalid operation, input or file error (for example a second `record`); 130/143 reports SIGINT/SIGTERM during dispatch. A partial final artifact is retained even with exit 1. Missing usage is unknown, not zero. Usage schemas and cached/reasoning counters differ; do not sum overlapping fields or claim a subscription dollar cost.
