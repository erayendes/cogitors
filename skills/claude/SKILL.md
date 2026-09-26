---
name: claude
description: Use when the user invokes /claude or explicitly asks Claude Code to perform a task. Not for ordinary coding requests or discussion of Claude.
---

# Claude

Run the user's task with Claude Code only. Do not start a council or delegate recursively. Preserve the task, working directory, account, requested model/effort and authorization scope.

If the current host is already the requested Claude instance, perform the task here unless the user requests a separate process, independent context or a different model/account. Never claim the current host changed model when it did not.

For an external call, read [execution](references/execution.md). Create a one-job JSON manifest with `agent: claude`, the absolute trusted project `cwd`, concise full task `prompt`, and `access: review` unless edits are authorized. Pass `model`/`effort` only when selected; otherwise inherit existing settings. Run the bundled `scripts/run.py` through Python. In a repository checkout, use `../cogitors/scripts/run.py` and `../cogitors/references/execution.md`; standalone packages contain their own copies.

Require installed/authenticated `claude`; report missing access without changing settings or providers. The adapter uses literal stdin, structured output, bounded execution and retained results. Plan mode is not an OS sandbox; retain host restrictions. Do not add bypass flags or `--bare` as a cost shortcut.

Read the normalized response, verify consequential claims and any changed artifacts with relevant checks, then give one concise result with remaining limitations. Missing usage is unknown. A timeout or provider error does not authorize a retry, another model or another account. For an explicitly requested follow-up, use the recorded session ID, never `-c` or the latest conversation.
