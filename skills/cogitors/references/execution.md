# Shared CLI execution

The packaged skills contain the same `scripts/run.py` adapter. In a source checkout it lives at `skills/cogitors/scripts/run.py`; the packager copies it and this reference into each standalone bundle. No other skill must be installed to use a single-agent bundle.

Requirements: Python 3.9+, macOS/Linux, an installed authenticated CLI for the selected external participant, and the host's normal network/credential access. Preserve the current account and environment. Do not install software, alter global settings, log in to another account or switch to a separately billed API without authorization.

## Check the actual execution context first

Run `python3 scripts/run.py --check /path/job.json` before a standalone call. The Cogitors uses `python3 scripts/cogitor.py check RUN_DIR`. Neither calls a model. Both execution entrypoints repeat this check before starting model processes: CLI presence, Codex/Claude login visibility, and Antigravity's local-port and runtime-log access. This checks startup prerequisites, not model availability, quota or answer quality.

In a restricted host, `operation not permitted`, a denied localhost bind, or `Not logged in` can mean the host sandbox hides an existing session. Request the host's normal approval to run the **exact check command** outside that sandbox. In Codex's execution tool, use `sandbox_permissions: require_escalated` with an explicit justification. If the approved check passes, request the same execution scope for the exact `dispatch` or standalone runner command. Permission does not carry over merely because a previous check succeeded. Never request a blanket Python/shell approval or change global sandbox settings; retain the provider's `--sandbox`/planning flags.

If the approved-context check still cannot see login, stop and ask the user to log in to the same CLI/account. Do not extract tokens, log out, switch accounts or fall back to an API. A preflight failure occurs before a paid dispatch marker: fixing access and checking again does not repeat a model call. Once a dispatch marker exists, preserve it; a failed run requires an explicitly authorized new run, not marker deletion or automatic retry.

Write JSON using the host's file tool; do not interpolate a raw prompt into shell source. For a single-agent skill, include exactly one job for that agent:

```json
{
  "jobs": [{
    "agent": "claude",
    "cwd": "/absolute/project",
    "prompt": "Review the specified proposal without edits. Give concise findings with evidence.",
    "access": "review",
    "timeout_seconds": 180,
    "model": "opus",
    "effort": "high"
  }]
}
```

`agent` is `codex`, `claude` or `antigravity`; `cwd` must exist and be absolute. Omit `model` and `effort` to inherit settings. Model names are passed literally, never guessed or silently replaced. Current effort options: Codex `low/medium/high/xhigh/max/ultra`; Claude `low/medium/high/xhigh/max`; Antigravity `low/medium/high/xhigh/max`. A model can still reject a CLI-supported effort. Report that incompatibility; do not fall back automatically.

```sh
python3 /actual/installed-skill/scripts/run.py /path/job.json
```

Use the host's background mechanism for long calls. Stdout returns paths and statuses; read the saved result's `response` and relevant metadata, not the complete event log. Results include requested model/effort (null means inherited, not a verified effective model), session ID, usage if supplied, exit code and a request hash. CLI success requires both successful exit and valid structured completion. Malformed, empty or error responses fail closed. There are no automatic retries or provider/account switches.

`access: review` is the default. `edit` is only for explicitly authorized work and file ownership. `context_only: true` means all necessary evidence is in the prompt and cannot combine with edit. It disables Claude tools/MCP and instructs all providers to use supplied context only. Those instructions are not a universal OS sandbox. No task may delegate recursively.

| Tool | Review | Authorized edit | Explicit selection |
|---|---|---|---|
| Codex | `exec --sandbox read-only --json -` | `workspace-write` | `--model`; `-c model_reasoning_effort=…` |
| Claude | `-p --permission-mode plan --output-format json` | `acceptEdits` | `--model`; `--effort` |
| Antigravity | `--mode plan --sandbox --output-format json -p …` | `accept-edits` | `--model`; `--effort` |

Command forms were checked with local help for codex-cli 0.159.3, Claude Code 2.1.286 and agy 1.3.1. Live provider/model availability is not implied. Inspect local help once on incompatibility. Do not add approval/sandbox bypass flags. Claude plan and Antigravity plan are not interchangeable OS read-only guarantees; any host exception needs the explicit approval above. Do not combine Antigravity plan with `--disable-slash-commands`. `--bare` is not a generic token-saving flag: it changes authentication behavior.

Timeout/interruption terminates only the launcher's own process groups. Already-started remote work or detached tools are not guaranteed cancelled. Retain successes, report failures and do not automatically resubmit. If a follow-up is explicitly requested, use this job's recorded ID with the CLI's documented resume command, never `--last`/`--continue`. The Cogitors' rounds use fresh bounded prompts instead.
