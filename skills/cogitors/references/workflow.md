# Host-assisted workflow

The Cogitors is a skill, not a new model service. The host supplies its own four advisor contributions and final synthesis. The script calls only the other two CLIs, at most once per advisor per round: at most eight external invocations, plus the host's work. Model-internal tool turns are not covered by this invocation count.

Use the actual installed script path. A shell that supports background jobs lets the host work while the other advisors run. `check`, `status`, `init`, `approve`, `record`, `advance` and `finish` never call a model. Only `dispatch` does. Do not directly run a round's jobs through the single-call adapter; that would bypass the no-repeat gate.

## 1. Initialize

Write the full assignment to a UTF-8 brief through the host's file tool. Include purpose, exact scope, allowed changes, expected deliverable and evidence requirements. The brief and selected source files form the shared snapshot. Select all relevant source files with repeated `--source`; uncaptured workspace files are not integrity-checked. All advisors still receive the complete task.

For empirical grounding, run tests, lint or static analysis yourself (with the user's approval, as for any command), save the output to a file and pass it with repeated `--evidence-file`. Every advisor sees it from round 1. Its text is hashed and frozen at `init`, so a temporary report may be deleted afterwards. Cogitors never runs commands itself. Evidence counts toward the 200000-character shared limit and toward `status.scope`; it is not redacted, so trim secrets, tokens and unrelated logs before passing it.

```sh
python3 /actual/cogitors/scripts/cogitor.py init /path/brief.md \
  --chair codex --cwd /path/project --source /path/project/proposal.md
```

The returned `run_dir` is a fresh private temporary directory. `--run-dir /new/directory` selects a persistent destination but refuses any existing directory. Paths are examples, not personal defaults. Immediately tell the user the returned `output_dir`.

By default, `init` targets a unique session subfolder named `<timestamp>-<slug>` under `CWD/docs/cogitors-decisions/`. Optional `--slug my-topic` specifies the slug; otherwise it is automatically extracted from the first heading or line of the brief. The folder is created on the first completed round, containing only `brief-<slug>.md`, `codex-<slug>.md`, `claude-<slug>.md`, `antigravity-<slug>.md` and, when finished, `decision-<slug>.md` and `decisions-<slug>.html`. Use `--output-dir` for another destination or `--private` when the user requests no exported files. These are model outputs, not automatically redacted public documents; review before committing. Jobs, raw logs, credentials, and state are never exported. An export failure retains private results and reports the problem; do not repeat model calls to repair file delivery.

Defaults: 180 seconds per external invocation and a 1800-second run dispatch deadline. `--timeout` (up to 3600) and `--total-timeout` honor an explicitly agreed time budget. The run deadline prevents starting remote work after expiry and caps remaining dispatch time; it cannot terminate the current host's own thinking. The host also respects the user's overall deadline.

### Model Discovery, Configuration & CLI Flags

The Cogitors provides native model inspection and configuration without requiring manual JSON authoring:

1. **Inspect Models & Detected CLIs (`models`)**:
   ```sh
   python3 scripts/cogitor.py models
   ```
   Lists all installed CLIs, authentication status, and recommended/available models (including dynamic discovery from `agy models`).

2. **Interactive Configuration (`configure`)**:
   ```sh
   python3 scripts/cogitor.py configure -i
   ```
   Interactive terminal menu (Heimdall-style) to choose preferred models and reasoning efforts for Codex, Claude, and Antigravity, saving them to `~/.cogitors/config.json` (or `.cogitors.json` via `--local`). Subsequent `init` commands automatically inherit these settings!

3. **Direct CLI Model Flags (`init` overrides)**:
   ```sh
   python3 scripts/cogitor.py init /path/brief.md --chair antigravity --cwd "$PWD" \
     --codex-model o3 --codex-effort high \
     --claude-model sonnet
   ```
   Directly pass `--codex-model`, `--codex-effort`, `--claude-model`, `--claude-effort`, `--antigravity-model`, or `--antigravity-effort`.

4. **Session Header Banner (`banner`)**:
   Every `init` prints a formatted council header banner to stderr and includes `banner` (ASCII box) and `banner_md` (Markdown table) in its result. It can also be viewed anytime:
   ```sh
   python3 scripts/cogitor.py banner /path/run [--markdown]
   ```

5. **Legacy JSON Options (`--options`)**:
   Optional `--options /path/options.json` continues to supply custom settings:
   ```json
   {"claude": {"model": "opus", "effort": "high"}, "codex": {"model": "o3", "effort": "high"}}
   ```
   Overrides for the current chair are automatically handled: the chair participates via its host session, while external advisors run their configured models.

## 2. Repeat advisor rounds 1–4

Before the first dispatch, show the user `status.scope` from `init`: providers, file count, bytes/characters, rounds, that peer answers are sent in rounds 2-4, `max_calls` and `max_calls_with_retries`. Ask once for explicit consent to that whole scope, then run `approve RUN_DIR`. `dispatch` refuses until approved; do not approve on the user's behalf.

First run `check RUN_DIR` in the context intended for dispatch. Follow [execution](execution.md) for narrowly approved host permissions if it fails. Each dispatch checks again before claiming its marker; failed checks spend no model tokens. An approved check does not grant future dispatch commands permission automatically.

1. Read `chair_prompt` from `status`. Start `dispatch RUN_DIR` as a host-managed background job, with the approved execution scope when required. Its stdout contains status metadata only, not peer answers.
2. Independently produce the chair's advisor contribution in a scratch file. In the first round, do not read any other advisor's output. In later rounds, use only the completed previous-round material provided in the prompt; do not read same-round peers early.
3. Run `record RUN_DIR --file /path/host-answer.md`. Recording is exclusive: a submitted view cannot be rewritten after seeing a peer.
4. Wait for the dispatch job to finish. On cancellation, stop. On a participant failure, inspect the status without retrying it.
5. Run `advance RUN_DIR`. It requires the host record, validates result provenance and source hashes, writes the advisor histories, and prepares the next round. Read only these normalized outputs when needed, not entire CLI logs.

Tell the user when each round starts and completes. If `advance` returns `awaiting-partial-decision`, report the round as paused, name the failed advisor and stop for the user's choice:

1. **Extend Timeout & Retry (`extend-timeout`) — Recommended for Timeouts:**
   ```sh
   python3 /actual/cogitors/scripts/cogitor.py extend-timeout /path/run --add 180
   ```
   Retries **only the timed-out or failed advisor** with an extended timeout without wasting tokens by re-running already successful peers. If it succeeds, the full 3-agent council is preserved!

2. **Continue with Remaining Panel (`continue-partial`):**
   ```sh
   python3 /actual/cogitors/scripts/cogitor.py continue-partial /path/run
   ```
   Drops the failed advisor and continues the deliberation with the surviving participants.

3. **Stop Deliberation (`stop`):**
   Running no further command halts the session; all generated artifacts remain preserved.

```sh
python3 /actual/cogitors/scripts/cogitor.py dispatch /path/run
python3 /actual/cogitors/scripts/cogitor.py record /path/run --file /path/host-answer.md
python3 /actual/cogitors/scripts/cogitor.py advance /path/run
```

The shell snippet shows command forms; start `dispatch` with the host's background mechanism so the chair can work concurrently. Alternatively, write the host answer first and run `cycle RUN_DIR --file /path/host-answer.md` to atomically record, dispatch and advance in one streamlined step.

After the user chooses `continue-partial`, two survivors continue through the same rounds with explicit partial coverage. A dropped advisor's earlier view remains evidence, never a final vote. Fewer than two survivors blocks the run. A source change also stops progression: do not mix versions or silently start the whole paid run again. Preserve artifacts and report the reason.

`status.next_action` names the single safe next step for the current state: a runnable `command`, or `command: null` with `ask_user` choices or a note. After a crash it offers no command while a `dispatched` marker has no results. `dispatched` markers deliberately survive crashes. A crash after starting a remote request cannot establish whether that request spent tokens; do not delete the marker or retry automatically. Ask before a new paid run. Partial local writes may require inspection rather than automatic recovery.

## 3. Synthesize once

After round 4, status is `ready`, round is `5`, and `synthesis.md` contains the original task, source snapshot, all four rounds, final views and failures. The chair reads it and writes JSON with four nonempty string fields:

```json
{
  "answer": "The supported recommendation or deliverable.",
  "agreement": "Which conclusions are shared, by whom; explicitly say when none are shared.",
  "dissent": "Reasoned minority positions and unresolved objections, or explicitly none.",
  "uncertainties": "Unverified assumptions, missing checks and limits."
}
```

```sh
python3 /actual/cogitors/scripts/cogitor.py finish /path/run --file /path/final.json
```

`decision-<slug>.md` adds actual participation coverage, a comparison matrix, and timing metrics. An interactive single-file `decisions-<slug>.html` report is also exported, adapting automatically to your device's dark or light theme, and containing deliberation history and direct "Download .md" and "Copy .md" buttons. Present one coherent output in the user's language, retaining the required distinctions, and provide the absolute `final` path returned by `finish`.

## Artifacts and exits

- `state.json`: settings, shared evidence, round results, raw provider usage when available.
- `brief-<slug>.md`, `codex-<slug>.md`, `claude-<slug>.md`, `antigravity-<slug>.md`: session brief and separate named histories, including failed/missing rounds.
- `round-N/`: chair prompt, immutable chair submission, prepared `jobs.json`, deadline-capped `dispatched-jobs.json`, dispatch marker, normalized results and private CLI logs. Prepared requests are hashed in state; changed jobs are rejected before execution.
- `synthesis.md`, `decision-<slug>.md`, `decisions-<slug>.html`: synthesis input, final decision outputs, and standalone HTML viewer.
- `output_dir` in status: optional project delivery folder; `export_error` reports delivery failures without discarding private results.

Exit 0 means the operation succeeded; 1 reports failed dispatch jobs, a blocked panel or a partial final result; 2 is an invalid operation/input; 130/143 reports SIGINT/SIGTERM during dispatch. A partial final artifact is retained even with exit 1. Missing usage is unknown, not zero. Usage schemas and cached/reasoning counters differ; do not sum overlapping fields or claim a subscription dollar cost.
