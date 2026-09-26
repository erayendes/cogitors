---
name: antigravity
description: Use when the user invokes /antigravity or explicitly asks Google Antigravity to perform a task. Not for ordinary coding requests or discussion of Antigravity.
---

# Antigravity

Run the user's task with Antigravity only. Do not start a council or delegate recursively. Preserve the task, working directory, account, requested model/effort and authorization scope.

If the current host is already the requested Antigravity instance, perform the task here unless the user requests a separate process, independent context or a different model/account. Never claim the current host changed model when it did not.

For an external call, read [execution](references/execution.md). Create a one-job JSON manifest with `agent: antigravity`, the absolute project `cwd`, concise full task `prompt`, and `access: review` unless edits are authorized. Pass `model`/`effort` only when selected; otherwise inherit existing settings. Run the bundled `scripts/run.py` through Python. In a repository checkout, use `../cogitor/scripts/run.py` and `../cogitor/references/execution.md`; standalone packages contain their own copies.

Require installed/authenticated `agy`; report missing access without changing settings or providers. The adapter passes the prompt as one literal argument, retains structured results and bounds execution. Plan mode and terminal restrictions are not a universal OS read-only boundary. Do not add bypass flags or combine plan with `--disable-slash-commands`.

Read the normalized response, verify consequential claims and any changed artifacts with relevant checks, then give one concise result with remaining limitations. Missing usage is unknown. A timeout or provider error does not authorize a retry, another model or another account. For an explicitly requested follow-up, use the recorded conversation ID, never `-c` or the latest conversation.
