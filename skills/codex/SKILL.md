---
name: codex
description: Use when the user invokes /codex or explicitly asks Codex to perform a task. Not for ordinary coding requests or discussion of Codex.
---

# Codex

Run the user's task with Codex only. Do not start a council or delegate recursively. Preserve the task, working directory, account, requested model/effort and authorization scope.

If the current host is already the requested Codex instance, perform the task here unless the user requests a separate process, independent context or a different model/account. Never claim the current host changed model when it did not.

For an external call, read [execution](references/execution.md). Create a one-job JSON manifest with `agent: codex`, the absolute project `cwd`, concise full task `prompt`, and `access: review` unless edits are authorized. Pass `model`/`effort` only when selected; otherwise inherit existing settings. Run the bundled `scripts/run.py` through Python. In a repository checkout, use `../cogitors/scripts/run.py` and `../cogitors/references/execution.md`; standalone packages contain their own copies.

Require installed/authenticated `codex`; report missing access without changing settings or providers. The adapter uses literal stdin, structured output, bounded execution and retained results. Do not replace it with shell-interpolated prompt text or bypass flags.

Read the normalized response, verify consequential claims and any changed artifacts with relevant checks, then give one concise result with remaining limitations. Missing usage is unknown. A timeout or provider error does not authorize a retry, another model or another account. For an explicitly requested follow-up, use the recorded session ID, not the account's latest session.
