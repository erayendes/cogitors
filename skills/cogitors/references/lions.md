# Lions

Shared by `/voltron` (parts of one job) and `/lions` (one task, several views). The host is the Elder; every other model and account is a **lion**. Keep raw lion output for verification. The Elder gives the user one summary from the checked reports.

## Who the lions are

`--elder` names the host's own lion: `codex`, `claude`, `agy`, or an account name when the host itself runs under that account's config directory (for example `claude-alt` when `CLAUDE_CONFIG_DIR` is `~/.claude-alt`). Another account of the Elder's CLI is still a lion; the built-in `codex` and `claude` lions always run on the default account.

Extra accounts are `accounts` entries in the user's global `~/.cogitors/config.json` only, each `{"agent": "codex" | "claude", "config_dir": "~/.codex-alt"}`. At most five lions run at once, like the five that form Voltron; `--exclude NAME` leaves one out.

## Quota

Run `cogitor.py quota --json` before planning, including for the Elder. Use `--cwd DIR` for the project. It reads local data without model calls, network access or token reads.

- Read the state for each lion and pool. `exhausted` means an active cooldown or an unreset window at 100%. `low` means a window is over 90% used and still has room. `ok` means known quota with room. `unknown` means no current window data: a window whose reset has passed is ignored, and with none left the state is `unknown`.
- Check `source` and `age_seconds`. The `five_hour` and `seven_day` windows give `used_percent` and `resets_at` (epoch seconds) when available. `codex-session` comes from local Codex session logs and needs no config. `statusline` comes from a Claude Code status-line snapshot. To use one, map the Claude lion to its path in the optional global `usage` section, for example `{"usage": {"claude": "~/.claude/statusline-usage.json"}}`. `cooldown` comes from the ledger and `none` means no source.
- Read `cooldown_until` for an active block in `~/.cogitors/quota.json`. Codex and Claude use an `account` pool. Antigravity uses separate pools for its quota groups. Use the model-to-group map from `quota --json`, derived from the group descriptions in Antigravity's quota summary and the display names in `agy models`. A lion without a model is checked against all its pools. With `{"usage": {"antigravity": "acp"}}` its windows are read (source `agy-acp`) from a short local `agy acp` session that makes no model call and leaves no conversation behind, at most once every five minutes; without it Antigravity has only cooldowns. The engine sets the cooldown to the reset in the error when available or to one hour from the failure, keeps a longer block already recorded for the pool, and treats a bare 429 or a throttle that clears within a minute as a plain failure. Codex readings come from the latest account-wide (`limit_id` `codex`) reading among the six newest session files. Expired cooldowns are ignored; deleting the file clears them all.

## Choosing models

1. **Pick the CLI or account by quota.** From `cogitor.py quota --json`, leave out `exhausted` lions and rank known room ahead of `unknown`. Among lions with room, give weekly windows priority over 5-hour windows, then prefer the window with room that resets soonest. A 5-hour window comes back within hours and unused weekly quota is lost. Use capability only to rule out a lion that cannot do the work. For simulator, emulator or GUI work, for example, the Codex sandbox cannot reach it.
2. **Pick the model and effort within that lion.** Use the live `cogitor.py models` list and match the size and risk of the work. Pick a strong model and high effort for design or hard reasoning, and a fast model and low effort for routine work. For Antigravity, use the model-to-group map to keep the choice within the pool you ranked.

Use `light` for routine or narrow work, `standard` for typical work, and `deep` for design or hard reasoning. The optional global `routing` section maps a tier and agent (`codex`, `claude` or `antigravity`) to a model and effort, for example `{"routing": {"light": {"codex": {"model": "gpt-6-luna", "effort": "low"}}}}`. A tier may instead be an ordered fallback list of lions, for example `{"routing": {"deep": [{"lion": "codex", "model": "gpt-6.2-astra", "effort": "high"}, {"lion": "claude", "model": "opus"}]}}`; `quota --json` shows it under `fallbacks` with each step's state. When a tier has a list, its order wins for the first choice and after a definite quota error. Take the first lion that can do the work, is not the Elder and is not `exhausted`. For `/lions`, skip families that already have a view. Without a list, use the dynamic order above. Use the validated routing returned by `quota --json`. Each `voltron` run appends one line per lion to `~/.cogitors/runs.jsonl` (settings, status, time, usage or `unknown`; never prompts, answers or errors); `cogitor.py metrics` summarizes it per lion and model.

For a review, prefer a model family other than the one that built the work.

For `/lions`, seek independent model families. Two accounts of the same CLI count as one family. If a family is out, run with fewer views and report the coverage.

## The plan

The Elder's quota is the scarcest resource. Before forming Voltron or sending lions, estimate the Elder's share for planning, joining and verification, roughly 5% for a small job or 15–20% for a big Voltron. Use the lowest remaining percentage among the Elder's active windows. Put the estimate and remaining quota in the plan line, for example `management ~15%, left 40%`. If the remaining quota is below the estimate or `unknown`, the Elder takes no part and assigns joining and verification to a lion in the plan. Include any shared scaffold work in that handoff.

Keep the Elder's use low. Ask lions for short structured reports and assign a lion to check raw diffs and long outputs.

Write a plan like this with the host's file tool, outside the project (for example in the system temp directory).

```json
{
  "mode": "parts",
  "task": "Context every lion shares: the job, constraints, conventions.",
  "lions": [
    {"name": "codex", "tier": "light", "task": "This lion's part.", "owns": ["server/payments"]},
    {"name": "claude", "model": "sonnet", "effort": "medium", "task": "Another part.", "owns": ["ui/checkout"]}
  ]
}
```

- `mode` is `parts` (each lion has its own `task`; `owns` lists the paths, relative to `--cwd`, it may change) or `same` (the top-level `task` goes to every lion; lions carry no `task`).
- A lion's optional `tier` fills `model` and `effort` from `routing[tier][agent]`, or from its own step when the tier is a list. Explicit plan values win per field. Use saved defaults for any model or effort still unset. A tier that `routing` does not define for that lion's agent (or, for a list, for that lion) is a plan error that names it.
- Lions not named in the plan do not run. The Elder is never a lion.
- Include only the task's own context, leaving out credentials and unrelated chat history.

## Announce and run

Start on an explicit request. If you propose forming Voltron or sending lions, get one yes covering the lions, accounts, access and a call ceiling. Honor a request to see the plan before dispatch. Before each dispatch, show one line per lion in the form `lion · account · model · effort · why`.

Record every proposal once the user answers with `cogitor.py proposal --kind KIND --answer ANSWER`. Use `voltron` or `lions` for `KIND` and `accepted` or `declined` for `ANSWER`. `cogitor.py metrics` summarizes the answers so the proposal threshold and the Elder's reserve can be tuned.

In a repository checkout the script is `skills/cogitors/scripts/cogitor.py`; packages contain their own copy under `scripts/`. Read [execution](execution.md) for sandbox and login checks.

```sh
python3 /actual/installed-skill/scripts/cogitor.py voltron --elder ELDER --plan /tmp/plan.json --cwd /project --access edit --timeout 1800
```

- `--check` (with the same `--plan`) checks every planned lion's login and calls no model. Both `voltron` and `voltron --check` reject an exhausted plan lion before any model runs and give its name and reset time. If a check fails, report the lion and reason, then drop it from the plan; `--exclude` only removes a lion from the pool. Without a plan, exhausted lions are skipped and listed under `skipped`.
- `review` access: lions read the project in their read-only or plan modes, which are not an OS-level guarantee. `edit` (needs a git repository): each lion gets its own detached git worktree from a snapshot of the working tree as it is now, uncommitted and untracked files included, starting in the same subdirectory as `--cwd`; the user's branch, index and files stay untouched.
- The timeout is per lion, at most 3600 seconds. Run in the background.
- The command exits 0 when at least one lion succeeded and 1 only when none did; either way the JSON on stdout is the result, and its `run_dir` is needed for cleanup.

## Read every result

Each job's `result_path` holds its `response`; a failed job's `status` (`failed`, `timeout`, `cancelled`) and `error` give the reason, with the CLI's own last message (a quota or login error, for example) after the exit code. For `edit`, each job has `diff_path` and `changed` (and `diff_error` when its diff could not be taken); in `parts` mode `outside_owns` lists files a lion changed outside its part. This step is done when every lion's result is read and every failed lion is named with its reason.

Within the approved scope and ceiling, choose or change each lion's tier, model and effort per step without asking again. Reassign work without asking, and only after a definite `quota` error. Refresh quota and plan a dispatch for the failed work with another capable lion, following the order above. In `same` mode, use a replacement from the same family if one is available. Name the replacement and why in its dispatch line. Leave timeouts, unknown outcomes and other failures as they are, and keep successful results.

Ask again for new parts or paths, changes to `outside_owns`, anything outward-facing, a separately billed API or a higher call ceiling.

Stay the manager. Report a change to your own effort only if the host confirms it. If the Elder runs out, let running lions finish and keep their results. Pause new dispatches, conflict resolution and `git apply` assigned to the Elder until it is back. A session cannot move to another account: to hand the work over, commit local work in progress first and give the new agent the same brief and what was done.

Apply a diff from the repository root with `git apply --check DIFF`, then `git apply DIFF`. Apply only what the user's request authorized and leave it uncommitted unless the user asks for a commit.

Finish with `cogitor.py voltron-clean RUN_DIR` for each run's `run_dir` after applying any diff. It deletes the worktrees, diffs and reports.
