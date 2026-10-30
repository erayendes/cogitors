---
name: voltron
description: Use when the user invokes /voltron or explicitly asks every model and account to do the same task separately. Not for a deliberation (use cogitors) or a single-agent task.
---

# Voltron

The host is the Elder. Every other **worker** does the same task on its own: the Codex, Claude and Antigravity CLIs plus each extra account in the cogitors config, minus the Elder's own session. Worker reports are raw input for the Elder: the Elder checks them and gives the user one answer.

## Workers

`--elder` names the host's own worker: `codex`, `claude`, `agy`, or an account name when the host itself runs under that account's config directory (for example `claudework` when `CLAUDE_CONFIG_DIR` is `~/.claude-work`). Another account of the Elder's CLI is still a worker; the built-in `codex` and `claude` workers always run on the default account.

Extra accounts are `accounts` entries in the user's global `~/.cogitors/config.json` only, each `{"agent": "codex" | "claude", "config_dir": "~/.codex-work"}` with an optional `model` and `effort`. Other workers use the saved cogitors models. The voltron command has no model or effort flags: when the user wants another model, say so and ask before changing their config. At most five workers run at once; `--exclude NAME` (repeatable) leaves a worker out.

## Run

In a repository checkout the script is `../cogitors/scripts/cogitor.py` and the execution reference is `../cogitors/references/execution.md`, both relative to this SKILL.md's directory; packages contain their own copies at `scripts/` and [execution](references/execution.md). Read the execution reference for sandbox and login checks.

1. **Choose access.** `review` for reading tasks (code review, analysis, questions): workers run in their read-only or plan modes, which are not an OS-level guarantee. `edit` (needs a git repository with a commit) when the task changes files: each worker gets its own detached git worktree from `HEAD`, starting in the same subdirectory as `--cwd`, and leaves its changes uncommitted. Those worktrees hold only committed work; when the result shows `dirty_checkout`, tell the user their uncommitted changes were not part of the task.
2. **Write the task file** outside the project, for example in the system temp directory, with the host's file tool: the user's task in their words, the scope, and the output the Elder needs back (for a review: findings with `file:line`, severity and evidence). Include only the task's own context, leaving out credentials and unrelated chat history.
3. **Check.** Run `cogitor.py voltron --elder ELDER --cwd /project --check`. It calls no model; its `workers` list is who will start. If a worker fails the check, nothing runs: name the worker and its reason, and offer `--exclude` for it.
4. **Start.** State the workers, the access and the timeout in one line, then run in the background:

   ```sh
   python3 /actual/installed-skill/scripts/cogitor.py voltron --elder ELDER --file /tmp/task.md --cwd /project --access review --timeout 900
   ```

   The timeout is per worker, at most 3600 seconds. Exit code 1 only means some worker failed; the JSON on stdout is still the result, and its `run_dir` is needed for cleanup.
5. **Read every result.** Each job's `result_path` holds its `response`; a failed job's `status` (`failed`, `timeout`, `cancelled`) and `error` give the reason. This step is done when every worker's response is read and every failed worker is named with its reason. Continue with the workers that succeeded; a failed worker stays failed, with no retry or substitute model.

## Answer

Give the user one answer in their language. Account for every finding: merged with its duplicates and counted by how many workers raised it (3/4), verified by the Elder, labeled as unconfirmed, or dropped with the reason. Show raw reports only when the user asks.

For `edit`, skip jobs whose `changed` is false or whose `status` is not `success`, and read any `diff_error`. Compare the rest by `diff_path`, pick or combine the best, then from the repository root run `git apply --check DIFF` and `git apply DIFF`, and verify with the project's own checks. Apply only what the user's task authorized, and leave it uncommitted unless the user asks for a commit.

Finish with `cogitor.py voltron-clean RUN_DIR` using the result's `run_dir`, after applying any diff; it deletes the worktrees, diffs and reports.
