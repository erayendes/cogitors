# Changelog

🇹🇷 [Türkçe](docs/CHANGELOG.tr.md)

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
