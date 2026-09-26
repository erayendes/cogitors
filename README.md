# Cogitor

Codex, Claude and Antigravity independently examine the same task, challenge each other, and produce one supported answer.

[![Yerli üretim](https://img.shields.io/badge/%F0%9F%A4%9D-YERL%C4%B0%20%C3%9CRET%C4%B0M-red)](https://github.com/erayendes)

## Four skills, two levels

| Invocation | Behavior |
|---|---|
| `/codex <task>` | Codex only. |
| `/claude <task>` | Claude Code only. |
| `/antigravity <task>` | Antigravity only. |
| `/cogitor <task>` | All three, using the five-round protocol below. |

These are skill invocations, not new shell commands. Hosts may use a different prefix (for example `$cogitor`) or natural-language skill selection. The invoking agent chairs the session **and participates**; it is not a fourth model. No extra copy of the chair is started.

Türkçe: Tekli skiller yalnız seçilen ajanı çağırır. Cogitor üç ajana da aynı işin tamamını verir; bağımsız analiz, yeniden değerlendirme, münazara ve nihai görüşlerden sonra başkan tek sonuç sunar. Görüş birliği doğruluk kanıtı değildir; gerekçeli azınlık görüşü korunur.

## Five rounds

1. **Independent analysis:** same complete task and shared source snapshot; no peer answers visible.
2. **Reconsideration:** read the initial views; state what changed or stayed unchanged and why.
3. **Debate:** challenge specific claims with evidence and questions.
4. **Final positions:** answer objections and submit a final view.
5. **Synthesis:** the chair combines the actual final positions, explicitly reporting agreement, dissent, uncertainty and participation.

The chair records its own contribution before consuming same-round peer answers. Each advisor gets a separate named Markdown history. Original source files remain unchanged during deliberation. For an authorized implementation task, the chair may apply and verify the agreed change afterward.

## Requirements and installation

- Python 3.9+ on macOS or Linux; no Python package dependencies.
- A Codex, Claude Code or Antigravity host with shell/background execution and file tools.
- Installed and authenticated `codex`, `claude` and `agy` CLIs for the external participants. A single-agent skill needs only its chosen CLI.
- Normal host network and credential permissions. No automatic installation, login switching or approval bypass.

Build all four self-contained bundles:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/package_skills.py --output dist
```

Each `dist/<name>/` is an installable skill folder; each `dist/<name>.skill` is the same folder in ZIP format. Copy the expanded folders into the skill directory supported by your host, preserving existing versions as backups, or use a host installer that accepts `.skill` archives. Reload the host's skill discovery. No installer runs automatically.

The packager refuses to overwrite nonempty output. For another build, select a new output directory. Single-agent source folders share the adapter/reference during packaging; install the built bundles, not an isolated raw single-agent folder. The implementation of the adapter is maintained only once.

## Use

```text
/codex Review the authentication change without edits.
/claude Analyze this proposal using the configured model.
/antigravity Find contradictions in this specification.
/cogitor Review this proposal together. Keep the source unchanged and show unresolved objections.
```

Specify model and effort in the task when needed. Omitted selections inherit the tool's configuration. Selection is per participant, never a hardcoded model release. The current chair's model must be selected in its host before starting. Unsupported choices fail visibly without trying another model or API.

The [Cogitor skill](skills/cogitor/SKILL.md) tells the host how to operate the [round controller](skills/cogitor/references/workflow.md). The [shared adapter contract](skills/cogitor/references/execution.md) documents one-agent calls and actual CLI permission limits.

Advisor histories and the final decision are saved under `PROJECT/docs/cogitors-decisions/<session>/` by default. You can select another output directory or request private-only artifacts. Private prompts, state and raw CLI logs remain outside the project; exported answers can still contain sensitive task content and are not committed automatically.

## Bounded cost and honest failures

- At most **eight external CLI invocations** for a full session: two advisors × four rounds. The chair supplies four views and one synthesis in the current host. Each invocation can contain multiple provider/tool turns; this is not an exact token or dollar cap.
- No recursive delegation, automatic retries, extra debate rounds, response cache or silent provider/account fallback.
- Failed advisors are not retried. With two survivors, the run pauses until the user chooses a **partial** continuation or stops; fewer than two blocks deliberation and retains evidence.
- Default external timeout: 180 seconds per call; dispatch deadline: 1800 seconds per run, configurable. A timeout pauses for the user's partial/stop decision. The host must also respect the user's overall budget.
- Recorded provider usage is retained as reported. Unknown usage is not zero; subscription quotas are not converted into fictional dollar costs.

## Safety and limits

Run artifacts are private temporary directories by default. They contain prompts, source excerpts and responses: do not commit or publish them. Selected sources are hashed and checked between rounds; unrelated workspace files are not snapshotted. Source changes stop progression instead of mixing versions.

Execution checks local CLI/login/runtime readiness before starting model calls. A sandbox can hide an existing login or block Antigravity's localhost server and log directory. The host requests explicit permission for the exact check/dispatch command; Cogitor never disables the global sandbox or changes accounts automatically. A successful preflight is not a model/quota availability guarantee.

The controller enforces sequencing and locks submitted host views, but cannot prevent a host from manually opening raw logs or prove that an LLM obeyed its instructions. Claude/Antigravity planning modes are not universal OS sandboxes. Keep the parent host's filesystem restrictions. Process cancellation stops owned local process groups, not necessarily remote work or detached tools.

The included `.github` policies and hardening helper come from the repository's starting template. Repository settings are not changed by Cogitor or its build.

## Development

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Tests use fake CLI executables and controlled model-boundary responses; they do not call providers. They exercise five-round data flow, host independence gates, final corrections, partial panels, request provenance, deadlines, literal prompt transport, settings, cancellation and portable packaging. Real model quality and account access require a separate, explicitly approved live trial.

Named after the contemplative minds in *Dune*. This is an independent project. Design inspiration: [claude-council](https://github.com/hex/claude-council), [cc-debate](https://github.com/STRML/cc-debate), [LLM Council](https://github.com/karpathy/llm-council), and [CouncilKit](https://github.com/albertofettucini/CouncilKit).

## License

MIT © [Eray Endes](https://github.com/erayendes)
