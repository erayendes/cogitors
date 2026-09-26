# Host-assisted workflow

The Cogitors is a skill, not a new model service. The host supplies its own four advisor contributions and final synthesis. The script calls only the other two CLIs, at most once per advisor per round: at most eight external invocations, plus the host's work. Model-internal tool turns are not covered by this invocation count.

Use the actual installed script path. A shell that supports background jobs lets the host work while the other advisors run. `check`, `status`, `init`, `record`, `advance` and `finish` never call a model. Only `dispatch` does. Do not directly run a round's jobs through the single-call adapter; that would bypass the no-repeat gate.

## 1. Initialize

Write the full assignment to a UTF-8 brief through the host's file tool. Include purpose, exact scope, allowed changes, expected deliverable and evidence requirements. The brief and selected source files form the shared snapshot. Select all relevant source files with repeated `--source`; uncaptured workspace files are not integrity-checked. All advisors still receive the complete task.

```sh
python3 /actual/cogitors/scripts/cogitor.py init /path/brief.md \
  --chair codex --cwd /path/project --source /path/project/proposal.md
```

The returned `run_dir` is a fresh private temporary directory. `--run-dir /new/directory` selects a persistent destination but refuses any existing directory. Paths are examples, not personal defaults. Immediately tell the user the returned `output_dir`.

By default, `init` targets a unique session subfolder named `<timestamp>-<slug>` under `CWD/docs/cogitors-decisions/`. Optional `--slug my-topic` specifies the slug; otherwise it is automatically extracted from the first heading or line of the brief. The folder is created on the first completed round, containing only `cogitor-codex-<slug>.md`, `cogitor-claude-<slug>.md`, `cogitor-antigravity-<slug>.md` and, when finished, `cogitor-final-<slug>.md`/`cogitor-final-<slug>.json`. Use `--output-dir` for another destination or `--private` when the user requests no exported files. These are model outputs, not automatically redacted public documents; review before committing. Jobs, raw logs, credentials, briefs and state are never exported. An export failure retains private results and reports the problem; do not repeat model calls to repair file delivery.

Defaults: 180 seconds per external invocation and a 1800-second run dispatch deadline. `--timeout` (up to 3600) and `--total-timeout` honor an explicitly agreed time budget. The run deadline prevents starting remote work after expiry and caps remaining dispatch time; it cannot terminate the current host's own thinking. The host also respects the user's overall deadline.

Optional `--options /path/options.json` supplies external advisor settings, for example:

```json
{"claude": {"model": "opus", "effort": "high"}, "antigravity": {"effort": "medium"}}
```

Use model IDs/aliases supported by the installed CLI and account. The example is not a model entitlement guarantee. No model list is hardcoded. Overrides for the current chair are rejected: choose the host model in the host before invoking The Cogitors. Unsupported settings fail without another paid attempt or fallback.

## 2. Repeat advisor rounds 1–4

First run `check RUN_DIR` in the context intended for dispatch. Follow [execution](execution.md) for narrowly approved host permissions if it fails. Each dispatch checks again before claiming its marker; failed checks spend no model tokens. An approved check does not grant future dispatch commands permission automatically.

1. Read `chair_prompt` from `status`. Start `dispatch RUN_DIR` as a host-managed background job, with the approved execution scope when required. Its stdout contains status metadata only, not peer answers.
2. Independently produce the chair's advisor contribution in a scratch file. In the first round, do not read any other advisor's output. In later rounds, use only the completed previous-round material provided in the prompt; do not read same-round peers early.
3. Run `record RUN_DIR --file /path/host-answer.md`. Recording is exclusive: a submitted view cannot be rewritten after seeing a peer.
4. Wait for the dispatch job to finish. On cancellation, stop. On a participant failure, inspect the status without retrying it.
5. Run `advance RUN_DIR`. It requires the host record, validates result provenance and source hashes, writes the advisor histories, and prepares the next round. Read only these normalized outputs when needed, not entire CLI logs.

Tell the user when each round starts and completes. If `advance` returns `awaiting-partial-decision`, report the round as paused, name the failed advisor and stop for the user's choice:

```sh
python3 /actual/cogitors/scripts/cogitor.py continue-partial /path/run
```

Choosing stop means running no further command; the paused artifacts remain available. Continuing never retries the failed call. Starting a new run with a longer `--timeout` is a separate paid run and requires explicit authorization.

```sh
python3 /actual/cogitors/scripts/cogitor.py dispatch /path/run
python3 /actual/cogitors/scripts/cogitor.py record /path/run --file /path/host-answer.md
python3 /actual/cogitors/scripts/cogitor.py advance /path/run
```

The shell snippet shows command forms; start `dispatch` with the host's background mechanism so the chair can work concurrently. Every invocation uses a fresh external session and bounded supplied context. Do not resume an account's latest session.

After the user chooses `continue-partial`, two survivors continue through the same rounds with explicit partial coverage. A dropped advisor's earlier view remains evidence, never a final vote. Fewer than two survivors blocks the run. A source change also stops progression: do not mix versions or silently start the whole paid run again. Preserve artifacts and report the reason.

`dispatched` markers deliberately survive crashes. A crash after starting a remote request cannot establish whether that request spent tokens; do not delete the marker or retry automatically. Ask before a new paid run. Partial local writes may require inspection rather than automatic recovery.

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

`cogitor-final-<slug>.md` adds actual participation coverage. `complete` means all three finished, not that their claims are true; `partial` means fewer than three finished. Present one coherent output in the user's language, retaining the required distinctions, and provide the absolute `final` path returned by `finish`. Do not add a separate model call to write this synthesis.

## Artifacts and exits

- `state.json`: settings, shared evidence, round results, raw provider usage when available.
- `cogitor-codex-<slug>.md`, `cogitor-claude-<slug>.md`, `cogitor-antigravity-<slug>.md`: separate named histories, including failed/missing rounds.
- `round-N/`: chair prompt, immutable chair submission, prepared `jobs.json`, deadline-capped `dispatched-jobs.json`, dispatch marker, normalized results and private CLI logs. Prepared requests are hashed in state; changed jobs are rejected before execution.
- `synthesis.md`, `cogitor-final-<slug>.json`, `cogitor-final-<slug>.md`: synthesis input and final output.
- `output_dir` in status: optional project delivery folder; `export_error` reports delivery failures without discarding private results.

Exit 0 means the operation succeeded; 1 reports failed dispatch jobs, a blocked panel or a partial final result; 2 is an invalid operation/input; 130/143 reports SIGINT/SIGTERM during dispatch. A partial final artifact is retained even with exit 1. Missing usage is unknown, not zero. Usage schemas and cached/reasoning counters differ; do not sum overlapping fields or claim a subscription dollar cost.
