---
name: codex
description: Use when the user invokes /codex or explicitly asks Codex to perform a task. Not for ordinary coding requests or discussion of Codex.
---

# Codex

Run the user's task with Codex only. Do not start a council or delegate recursively. Preserve the task, working directory, account, requested model/effort and authorization scope.

If the current host is already the requested Codex instance, perform the task here unless the user requests a separate process, independent context or a different model/account. Never claim the current host changed model when it did not.

For an external call in a repository checkout, read `../cogitors/references/execution.md` and run `../cogitors/scripts/run.py` through Python, both relative to this SKILL.md's directory; packaged skills contain their own copies. Write a one-job JSON manifest outside the project, e.g. in a temporary directory, with `agent: codex`, the absolute project `cwd`, concise full task `prompt`, `access: review` unless edits are authorized, and `timeout_seconds` set to fit the task, up to 3600. Pass `model`/`effort` only when selected; otherwise inherit existing settings. An optional first token selects them: `/codex gpt-5.5-high <task>`. Treat the first token as a selection only if it is an effort word or a model-like ID containing a digit (`gpt-5.5`, `o3`); otherwise it is part of the task. Split a trailing effort (`low|medium|high|xhigh|max|ultra`) from the model; either part may be omitted (`/codex high <task>`). Pass the model literally.

Require installed/authenticated `codex`; report missing access without changing settings or providers. Call Codex only through `run.py` with a manifest written by the file tool, and keep its flags as they are.

Read the normalized response, verify consequential claims and any changed artifacts with relevant checks, then give one concise result with remaining limitations. Missing usage is unknown. A timeout or provider error does not authorize a retry, another model or another account. For an explicitly requested follow-up, use the recorded session ID, not the account's latest session.
