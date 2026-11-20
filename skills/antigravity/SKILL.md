---
name: antigravity
description: Use when the user invokes /antigravity or explicitly asks Google Antigravity to perform a task. Not for ordinary coding requests or discussion of Antigravity.
---

# Antigravity

Run the user's task with Antigravity only. Do not start a council or delegate recursively. Preserve the task, working directory, account, requested model/effort and authorization scope, unless its quota runs out (see below).

If the current host is already the requested Antigravity instance, perform the task here unless the user requests a separate process, independent context or a different model/account. Never claim the current host changed model when it did not.

For an external call in a repository checkout, read `../cogitors/references/execution.md` and run `../cogitors/scripts/run.py` through Python, both relative to this SKILL.md's directory; packaged skills contain their own copies. Write a one-job JSON manifest outside the project, e.g. in a temporary directory, with `agent: antigravity`, the absolute project `cwd`, concise full task `prompt` under 250 000 bytes, `access: review` unless edits are authorized, and `timeout_seconds` set to fit the task, up to 3600. Pass `model`/`effort` only when selected; otherwise inherit existing settings. An optional first token selects them: `/antigravity gemini-3.1-pro-high <task>` → model `gemini-3.1-pro-high`. Treat the first token as a selection only if it is an effort word or a model-like ID containing a digit; otherwise it is part of the task. If the whole token is a model listed by `agy models`, pass it unsplit as the model; otherwise split a trailing effort (`low|medium|high|xhigh|max`) from the model; either part may be omitted (`/antigravity high <task>`). Pass the model literally.

Require installed/authenticated `agy`; report missing access without changing settings or providers. Call Antigravity only through `run.py` with a manifest written by the file tool, and keep its flags as they are. Plan mode and terminal restrictions are not a universal OS read-only boundary.

Read the normalized response, verify consequential claims and any changed artifacts with relevant checks, then give one concise result with remaining limitations. Missing usage is unknown. A timeout or another provider error does not authorize a retry. A definite quota error does: without asking, rerun the task once on another capable model, account or CLI that has room (when the cogitors engine is installed, read `cogitors quota`: leave out any that cannot do the work, take the one with room whose window resets soonest, weekly windows first, then pick its model and effort by the work's size), and name the replacement and why in your next status line. For an explicitly requested follow-up, use the recorded conversation ID, never `-c` or the latest conversation.
