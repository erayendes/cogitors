---
name: claude
description: Use when the user invokes /claude or explicitly asks Claude Code to perform a task. Not for ordinary coding requests or discussion of Claude.
---

# Claude

Run the user's task with Claude Code only. Do not start a council or delegate recursively. Preserve the task, working directory, account, requested model/effort and authorization scope.

If the current host is already the requested Claude instance, perform the task here unless the user requests a separate process, independent context or a different model/account. Never claim the current host changed model when it did not.

For an external call in a repository checkout, read `../cogitors/references/execution.md` and run `../cogitors/scripts/run.py` through Python, both relative to this SKILL.md's directory; packaged skills contain their own copies. Write a one-job JSON manifest outside the project, e.g. in a temporary directory, with `agent: claude`, the absolute project `cwd`, concise full task `prompt`, `access: review` unless edits are authorized, and `timeout_seconds` set to fit the task, up to 3600. Pass `model`/`effort` only when selected; otherwise inherit existing settings. An optional first token selects them: `/claude opus-5.5-high <task>`. Treat the first token as a selection only if it is an effort word, a known alias (`opus|sonnet|haiku`) or a model-like ID containing a digit (`opus-5.5`); otherwise it is part of the task. Split a trailing effort (`low|medium|high|xhigh|max`) from the model; either part may be omitted (`/claude high <task>`). `opus`, `sonnet` and `haiku` pass as aliases; a versioned name becomes the full ID with dots as hyphens and a `claude-` prefix (`opus-5.5` → `claude-opus-5-5`).

Require installed/authenticated `claude`; report missing access without changing settings or providers. Call Claude Code only through `run.py` with a manifest written by the file tool, and keep its flags as they are. Plan mode is not an OS sandbox; retain host restrictions.

Read the normalized response, verify consequential claims and any changed artifacts with relevant checks, then give one concise result with remaining limitations. Missing usage is unknown. A timeout or provider error does not authorize a retry, another model or another account. For an explicitly requested follow-up, use the recorded session ID, never `-c` or the latest conversation.
