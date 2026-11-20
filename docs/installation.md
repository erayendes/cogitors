# Installation

🇹🇷 [Türkçe](installation.tr.md) · [← README](../README.md)

## Quick Install

```sh
npx skills add erayendes/cogitors
```

Install all six skills; `/codex`, `/claude`, `/antigravity`, `/voltron` and `/lions` use the `cogitors` engine.

## Requirements

* Python 3.9+ (macOS or Linux). **No external pip dependencies.**
* The `codex`, `claude` and `agy` CLIs installed and signed in (two agents are enough for a two-member council).

## Extra Accounts (Voltron)

`/voltron` and `/lions` run every CLI except the Black Lion's own session (the agent you talk to). To add a second login of Claude or Codex as its own lion, point it at that login's config directory in `~/.cogitors/config.json`. Accounts are read only from this global file, never from a project's `.cogitors.json`, so a cloned repository cannot choose which account directory a CLI loads:

```json
{"accounts": {"claude-alt": {"agent": "claude", "config_dir": "~/.claude-alt"},
              "codex-alt": {"agent": "codex", "config_dir": "~/.codex-alt"}}}
```

An account may also set its own `model` and `effort`; otherwise it uses the saved models. At most four lions run at once: with the Black Lion they are the five that form Voltron; `--exclude NAME` leaves one out. `cogitor.py voltron --black-lion claude --check` lists the lions and checks their logins without calling a model.

## Quota and Routing (optional)

`cogitor.py quota [--json]` shows each lion's remaining quota. It calls no model, uses no network and reads no token. Two optional sections of `~/.cogitors/config.json` feed it:

```json
{"usage": {"claude": "~/.claude/statusline-usage.json"},
 "routing": {"light": {"codex": {"model": "gpt-6-luna", "effort": "low"}},
             "deep": {"codex": {"model": "gpt-6.2-astra", "effort": "high"}}}}
```

* `usage` maps a Claude lion (`claude` or a Claude account) to a Claude Code status-line JSON snapshot that your status line writes. It holds `rate_limits.five_hour` and `rate_limits.seven_day`, each with `used_percentage` and `resets_at` (epoch seconds); either window may be missing. The status line runs only in interactive sessions, so an account used only as a lion keeps an old snapshot and reads as `unknown`; give each account its own path (for example by `CLAUDE_CONFIG_DIR`).
* `routing` maps a tier (`light`, `standard`, `deep`) and an agent (`codex`, `claude`, `antigravity`) to a `model` and `effort`; every field is optional. A plan lion with a `tier` gets its model and effort from here; an explicit `model` or `effort` in the plan wins. A tier can also be an ordered fallback list, `[{"lion": "codex", "model": "...", "effort": "high"}, {"lion": "claude", "model": "opus"}]`: a plan lion takes its own step's settings, and after a definite quota error the Black Lion moves the part to the first step that is not exhausted and not the Black Lion itself. A list's order wins over the soonest-reset preference. `quota --json` shows each list under `fallbacks`.
* Codex needs no setting: its quota is the latest account-wide reading (`limit_id` `codex`) among the six newest `rollout-*.jsonl` files under `sessions/` in `~/.codex` for the built-in `codex` lion, or in the account's `config_dir`.
* Antigravity: add `"antigravity": "acp"` to `usage` to read its quota. The engine starts `agy acp` for about two seconds, asks agy's local language server for its own quota summary (no model call, no token read; agy itself contacts its service), removes the empty session and caches the result for five minutes in `~/.cogitors/agy-quota.json`. The model-to-quota-group map is derived from agy's own quota summary and `agy models` display names rather than hard-coded model names, so new models land in the right group automatically. Without it, only cooldowns apply.
* When a lion hits a definite quota error, the engine records a cooldown in `~/.cogitors/quota.json` (mode 0600), using the reset time from the error text, or one hour if it gives none; a longer block already recorded is kept, and a bare 429 or a throttle that clears within a minute records nothing. It stores only the quota phrase, not the full error. Expired cooldowns are ignored; delete the file to clear them all.

`cogitor.py voltron` refuses a plan lion whose quota is exhausted before any model runs. Each run appends one line per lion to `~/.cogitors/runs.jsonl` (settings, status, duration, usage or `unknown`; never prompts, answers or error text). Each `/voltron` or `/lions` proposal and the user's answer are logged with `cogitor.py proposal --kind voltron|lions --answer accepted|declined`, so the proposal threshold and the Black Lion's reserve can be tuned from data. `cogitor.py metrics` summarizes runs as average time, success and quota rates per lion and model, and reports accepted and declined counts by kind under `proposals`.

## Diagnostics (Doctor)

To confirm every CLI is installed, signed in and ready for a council session:

```sh
npx cogitors doctor
```

`npx cogitors` is a thin npm launcher for the engine (Python 3.9+ is still required). Every subcommand works the same way. Set `COGITORS_PYTHON` to use a different Python. In a repository checkout, the same commands also run as `python3 skills/cogitors/scripts/cogitor.py <command>`.

## Model Selection

1. **List installed models:**
   ```sh
   npx cogitors models
   ```
   Lists the installed CLIs (`codex`, `claude`, `agy`) and all available models (including the dynamic `agy models` list).

2. **Interactive model picker:**
   ```sh
   npx cogitors configure -i
   ```
   A numbered terminal menu lets you choose the model and reasoning effort for Codex, Claude and Antigravity. The choices are saved to `~/.cogitors/config.json` as your default profile, and every later session uses them.

3. **Direct CLI flags:**
   ```sh
   npx cogitors init /path/brief.md --chair antigravity --cwd "$PWD" \
     --codex-model o3 --codex-effort high \
     --claude-model sonnet
   ```

## Session Header

Every `init` shows a header in the terminal and chat that summarizes the Elder, topic, council members, their models and the working directory. You can show it again at any time:

```sh
npx cogitors banner /path/run [--markdown]
```

## Manual Install (Build)

To build the six standalone skill packages, clone the repository and run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

This produces 6 installable folders (`cogitors`, `codex`, `claude`, `antigravity`, `voltron`, `lions`) under `dist/` and a `.skill` zip archive for each. Copy the built folders into your agent's skill directory:

| Agent / Host | Skill Directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/config/skills/` |
| Agent Skills Standard | `~/.agents/skills/` |
