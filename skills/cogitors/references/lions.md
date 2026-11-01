# Lions

Shared by `/voltron` (parts of one job) and `/lions` (one task, several views). The host is the Elder; every other model and account is a **lion**. Lion output is raw input for the Elder, never for the user: the Elder checks it and gives the user one summary.

## Who the lions are

`--elder` names the host's own lion: `codex`, `claude`, `agy`, or an account name when the host itself runs under that account's config directory (for example `claudework` when `CLAUDE_CONFIG_DIR` is `~/.claude-work`). Another account of the Elder's CLI is still a lion; the built-in `codex` and `claude` lions always run on the default account.

Extra accounts are `accounts` entries in the user's global `~/.cogitors/config.json` only, each `{"agent": "codex" | "claude", "config_dir": "~/.codex-work"}`. At most five lions run at once, like the five that form Voltron; `--exclude NAME` leaves one out.

## Choosing models

`cogitor.py models` lists each CLI's current models and efforts; Codex and Antigravity read them live from their CLIs. Pick a model and effort per lion to fit its work: the strongest model and a higher effort for design or hard reasoning, a fast model for routine or narrow work, different model families when independent views matter. A lion without a choice uses the saved cogitors models.

## The plan

Write the plan with the host's file tool, outside the project (for example in the system temp directory):

```json
{
  "mode": "parts",
  "task": "Context every lion shares: the job, constraints, conventions.",
  "lions": [
    {"name": "codex", "model": "gpt-6.1-sol", "effort": "high", "task": "This lion's part.", "owns": ["server/payments"]},
    {"name": "agy", "model": "gemini-3.8-flash-high", "task": "Another part.", "owns": ["ui/checkout"]}
  ]
}
```

- `mode` is `parts` (each lion has its own `task`; `owns` lists the paths, relative to `--cwd`, it may change) or `same` (the top-level `task` goes to every lion; lions carry no `task`).
- Lions not named in the plan do not run. The Elder is never a lion.
- Include only the task's own context, leaving out credentials and unrelated chat history.

## Announce and run

Show the plan in one short block: each lion, model, effort and its work. Start right away; wait for the user only when they asked to see the plan first. The user may interrupt to change a lion, model or part; stop and rerun only that part.

In a repository checkout the script is `skills/cogitors/scripts/cogitor.py`; packages contain their own copy under `scripts/`. Read [execution](execution.md) for sandbox and login checks.

```sh
python3 /actual/installed-skill/scripts/cogitor.py voltron --elder ELDER --plan /tmp/plan.json --cwd /project --access edit --timeout 1800
```

- `--check` (with the same `--plan`) checks every planned lion's login and calls no model. If a lion fails it, nothing runs: name the lion and its reason, then drop it from the plan or `--exclude` it.
- `review` access: lions read the project in their read-only or plan modes, which are not an OS-level guarantee. `edit` (needs a git repository): each lion gets its own detached git worktree from a snapshot of the working tree as it is now, uncommitted and untracked files included, starting in the same subdirectory as `--cwd`; the user's branch, index and files stay untouched.
- The timeout is per lion, at most 3600 seconds. Run in the background.
- The command exits 0 when at least one lion succeeded and 1 only when none did; either way the JSON on stdout is the result, and its `run_dir` is needed for cleanup.

## Read every result

Each job's `result_path` holds its `response`; a failed job's `status` (`failed`, `timeout`, `cancelled`) and `error` give the reason, with the CLI's own last message (a quota or login error, for example) after the exit code. For `edit`, each job has `diff_path` and `changed` (and `diff_error` when its diff could not be taken); in `parts` mode `outside_owns` lists files a lion changed outside its part. This step is done when every lion's result is read and every failed lion is named with its reason.

A job marked `quota` hit its model's quota or rate limit. Rerun that lion's part once, on another model of the same CLI that `cogitor.py models` lists (for example `gemini-3.8-flash-high` when `gemini-4-argon-high` is out), with a plan holding only that lion, and tell the user which model replaced which and why. Clean both runs when done. Every other failure stays failed: name it, and continue with the lions that succeeded.

Apply a diff from the repository root with `git apply --check DIFF`, then `git apply DIFF`. Apply only what the user's request authorized and leave it uncommitted unless the user asks for a commit.

Finish with `cogitor.py voltron-clean RUN_DIR` using the result's `run_dir`, after applying any diff; it deletes the worktrees, diffs and reports.
