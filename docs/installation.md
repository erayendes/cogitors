# Installation

🇹🇷 [Türkçe](installation.tr.md) · [← README](../README.md)

## Quick Install

```sh
npx skills add erayendes/cogitors
```

Install all four skills; `/codex`, `/claude` and `/antigravity` use the `cogitors` engine.

## Requirements

* Python 3.9+ (macOS or Linux). **No external pip dependencies.**
* The `codex`, `claude` and `agy` CLIs installed and signed in (two agents are enough for a two-member council).

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

To build the four standalone skill packages, clone the repository and run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

This produces 4 installable folders (`cogitors`, `codex`, `claude`, `antigravity`) under `dist/` and a `.skill` zip archive for each. Copy the built folders into your agent's skill directory:

| Agent / Host | Skill Directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity | `~/.gemini/config/skills/` |
| Agent Skills Standard | `~/.agents/skills/` |
