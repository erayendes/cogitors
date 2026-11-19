# Lions

Shared by `/voltron` (parts of one job) and `/lions` (one task, several views). The host is the Elder; every other model and account is a **lion**. Lion output is raw input for the Elder, never for the user: the Elder checks it and gives the user one summary.

## Who the lions are

`--elder` names the host's own lion: `codex`, `claude`, `agy`, or an account name when the host itself runs under that account's config directory (for example `claude-alt` when `CLAUDE_CONFIG_DIR` is `~/.claude-alt`). Another account of the Elder's CLI is still a lion; the built-in `codex` and `claude` lions always run on the default account.

Extra accounts are `accounts` entries in the user's global `~/.cogitors/config.json` only, each `{"agent": "codex" | "claude", "config_dir": "~/.codex-alt"}`. At most five lions run at once, like the five that form Voltron; `--exclude NAME` leaves one out.

## Quota

Run `cogitor.py quota --json` before planning, including for the Elder. Use `--cwd DIR` for the project. It reads local data without model calls, network access or token reads.

- Read the state for each lion and pool. `exhausted` means an active cooldown or an unreset window at 100%. `low` means a window has under 10% left. `ok` means known quota with room. `unknown` means no current window data: a window whose reset has passed is ignored, and with none left the state is `unknown`.
- Check `source` and `age_seconds`. The `five_hour` and `seven_day` windows give `used_percent` and `resets_at` (epoch seconds) when available. `codex-session` comes from local Codex session logs and needs no config. `statusline` comes from a Claude Code status-line snapshot. To use one, map the Claude lion to its path in the optional global `usage` section, for example `{"usage": {"claude": "~/.claude/statusline-usage.json"}}`. `cooldown` comes from the ledger and `none` means no source.
- Read `cooldown_until` for an active block in `~/.cogitors/quota.json`. Codex and Claude use an `account` pool. Antigravity has only cooldowns, in the `claude`, `gemini` or `other` model pool; a lion without a model is checked against all three. The engine sets the cooldown to the reset in the error when available or to one hour from the failure, keeps a longer block already recorded for the pool, and treats a bare 429 or a throttle that clears within a minute as a plain failure. Codex readings come from the latest account-wide (`limit_id` `codex`) reading among the six newest session files. Expired cooldowns are ignored; deleting the file clears them all.

## Choosing models

`cogitor.py models` lists each CLI's current models and efforts. Match capability to the work first. Among capable lions with known room, prefer the one whose window with room resets soonest. Consider `unknown` after known quota with room and leave out `exhausted` lions.

Use `light` for routine or narrow work, `standard` for typical work, and `deep` for design or hard reasoning. The optional global `routing` section maps a tier and agent (`codex`, `claude` or `antigravity`) to a model and effort, for example `{"routing": {"light": {"codex": {"model": "gpt-6-luna", "effort": "low"}}}}`. A tier may instead be an ordered fallback list of lions, for example `{"routing": {"deep": [{"lion": "codex", "model": "gpt-6.2-astra", "effort": "high"}, {"lion": "claude", "model": "opus"}]}}`; `quota --json` shows it under `fallbacks` with each step's state. When a tier has a list, its order wins over the soonest-reset rule, for the first choice and after a definite quota error: take the first step that is not the Elder and not `exhausted` (for `/lions`, also not a family that already has a view). Without a list, use the dynamic order above. Use the validated routing returned by `quota --json`. Each `voltron` run appends one line per lion to `~/.cogitors/runs.jsonl` (settings, status, time, usage or `unknown`; never prompts, answers or errors); `cogitor.py metrics` summarizes it per lion and model.

For `/lions`, seek independent model families. Two accounts of the same CLI count as one family. If a family is out, run with fewer views and report the coverage.

## The plan

Write the plan with the host's file tool, outside the project (for example in the system temp directory):

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

Within the approved scope and ceiling, choose or change each lion's tier, model and effort per step without asking again. Reassign work only after a definite `quota` error. Refresh quota and plan a dispatch for the failed work with another capable lion, following the order above. In `same` mode, use a replacement from the same family if one is available. Name the replacement and why in its dispatch line. Leave timeouts, unknown outcomes and other failures as they are, and keep successful results.

Ask again for new parts or paths, changes to `outside_owns`, anything outward-facing, a separately billed API or a higher call ceiling.

Stay the manager. Take no part yourself when either Elder window has under 10% left or the Elder's quota is unknown; writing the shared scaffold and joining are management work and stay yours. Report a change to your own effort only if the host confirms it. If the Elder runs out, let running lions finish and keep their results. Pause new dispatches, conflict resolution and `git apply` until the Elder is back.

Apply a diff from the repository root with `git apply --check DIFF`, then `git apply DIFF`. Apply only what the user's request authorized and leave it uncommitted unless the user asks for a commit.

Finish with `cogitor.py voltron-clean RUN_DIR` for each run's `run_dir` after applying any diff. It deletes the worktrees, diffs and reports.
