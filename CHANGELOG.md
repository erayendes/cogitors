# Changelog

🇹🇷 [Türkçe](docs/CHANGELOG.tr.md)

## Unreleased

### Added
- `cogitors quota` shows each lion's remaining quota without a model call, network or token read. Claude lions read a status-line snapshot (`usage` in `~/.cogitors/config.json`), Codex lions the latest account-wide reading of their newest session files; Antigravity only has cooldowns.
- A quota ledger, `~/.cogitors/quota.json`, records a cooldown when a lion hits a definite quota error.
- Routing tiers: a plan lion may carry `tier` (`light`, `standard`, `deep`); its model and effort come from `routing` in the config unless the plan sets them.
- `/voltron` and `/lions` may be proposed by the Elder on its own, but it asks first.
- A routing tier may be an ordered fallback list of lions; `quota --json` shows each step's state under `fallbacks`.
- Each `voltron` run appends one line per lion to `~/.cogitors/runs.jsonl` (no prompts, answers or errors); `cogitors metrics` summarizes time, success and quota rates per lion and model.
- `/voltron` and `/lions` briefs carry handoff contracts and name what does not count as done; only a finding backed by evidence blocks, and agreement within one model family is not verification.

### Changed
- `cogitors voltron` refuses a lion whose quota is exhausted, naming the lion and its reset time, before any model runs.
- A lion's part after a definite quota error goes to another capable lion with room (another account of the same CLI included), not only to another model of the same CLI.
- A failed Codex run now reports Codex's own error message instead of a closing stderr line.
- An old-style config (bare `{agent: options}`) keeps its saved models when `usage` or `routing` is added beside them.
- Antigravity's offline fallback model list no longer defaults to Argon; the default is `gemini-4-neon-high`.
- `cogitors` itself stays strict: no automatic retry, no model or account switch.

## 0.2.2

### Changed
- A lion that fails now reports its CLI's own last message, such as a quota error, not only an exit code.
- `cogitors voltron` exits 0 when at least one lion succeeded, so a partial run no longer looks like a failure.
- `/voltron` always speaks of forming Voltron.
- A lion that hits its model's quota is marked `quota`; the Elder reruns its part once on another model of the same CLI and says so.

## 0.2.1

### New
- **/lions:** Every other model and account does the same task from its own view; the Elder merges what they find. This is how `/voltron` worked in 0.2.0.
- **Plans with models:** For `/voltron` and `/lions` the Elder writes a plan that names each lion's model, effort and work, shows it and starts at once. `cogitors voltron --plan` runs it.
- **Current model lists:** `cogitors models` reads Codex's and Antigravity's models from their CLIs; the Claude list uses the current aliases.

### Changed
- **/voltron** now splits the job into parts: each lion builds one part within its own paths, and the Elder joins the parts and runs the checks. Files a lion changed outside its part are reported.
- Lions that edit start from a snapshot of the working tree, uncommitted and untracked files included, so the Elder can lay shared groundwork first without a commit.

## 0.2.0

### New
- **/voltron:** Gives the same task to every model and account except the Elder at once; each one works as a lion. The Elder checks their reports and gives one answer. Tasks that change files run in a separate git worktree per lion. Second Claude or Codex logins are listed as `accounts` in `~/.cogitors/config.json`.
- **Follow-up questions:** Every part of the HTML report has an **Ask** button. Copy questions one at a time or as a list and paste them into the chat. The Elder answers from the session record without calling a model, and the answers appear under the part you asked about. The decision text never changes.
- **Revisit:** The Elder can set a date to revisit the decision. `cogitors revisit` lists the sessions whose date has come. Each reasoned dissent can also say what would settle it.
- **Screening before a session:** When the decision is already made, when only confirmation is wanted, or when there are no concrete options, the Elder says so before any model call.

### Changed
- Sessions now live in `docs/cogitors/<time>-<slug>/` instead of `docs/cogitors-decisions/`. Working files stay in a `temp/` folder that git never sees and are deleted when the report is finished.
- Extra accounts are read only from the global config file; a cloned repository cannot choose an account directory.
- `configure -i` and `init -i` need a terminal instead of silently falling back to fixed models.

### Fixed
- `--git-diff HEAD` now includes staged changes.
- A timeout retry can run again after its login check failed.
- Altered or added jobs are rejected.
- `next_action` offers recording the Elder's own view while a dispatch is running.
- Antigravity model IDs (`gemini-3.1-pro-high`) are no longer split.
- Packaging works when the output's parent folder does not exist.
