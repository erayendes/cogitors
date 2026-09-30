# The Cogitors

> "The eyes of common perception do not see far. Too often we make the most important decisions based only on superficial information."
>
> — Cogitor Kwyna

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img alt="The Cogitors" src="assets/logo.svg" width="420">
  </picture>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://milowda.com"><img alt="Yerli üretim" src="https://img.shields.io/badge/YERL%C4%B0%20%C3%9CRET%C4%B0M-red?style=flat&label=%F0%9F%A4%9D&color=red&link=https%3A%2F%2Fmilowda.com"></a>
  <a href="https://github.com/erayendes/cogitors/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/erayendes/cogitors/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://www.npmjs.com/package/cogitors"><img alt="npm" src="https://img.shields.io/npm/v/cogitors.svg"></a>
  <img alt="Python: 3.9+" src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-0-brightgreen.svg">
  <a href="https://agentskills.io"><img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-compatible-purple.svg"></a>
</p>

🇹🇷 [Türkçe](docs/README.tr.md)

---

When a critical architecture choice, security review or product decision is on the line, consulting a single AI is risky: a model cannot see its own hallucinations, biases and blind spots, and **it can defend flawed assumptions with complete confidence.**

## Three Models

**The Cogitors** brings three model families — **Codex (OpenAI)**, **Claude (Anthropic)** and **Antigravity (Google)** — to one deliberation table.
Every model receives the whole task. Over four rounds they analyze independently, read each other's views and answer objections with evidence. In round five the Elder synthesizes one reasoned decision.

> **Core principle:** Consensus is not proof of correctness.
> Reasoned minority views and uncertainties are never suppressed; they are preserved in the final decision.

---

## Four Skills

`/<model> <task>` calls Codex, Antigravity or Claude onto a task, and it gets the job done in the background.

`/cogitors <task>` is different: it starts the five-round deliberation protocol with all three agents.

```text
- /antigravity Find the contradicting clauses in this technical spec.
- /claude Analyze the performance bottlenecks in this PR diff.
- /codex List the weaknesses in the authentication flow without changing code.

- /cogitors Review this architecture proposal together. Do not change any code, and state unresolved objections explicitly.
- /cogitors --git-diff HEAD~1 Deliberate on this PR's changes for security and performance.
```

> [!NOTE]
> These are not new terminal commands but standard **Agent Skills** invocations. The agent that starts the session becomes the **Elder**, runs it **and takes part in the deliberation itself**; no extra fourth model is launched.

---

## Five Rounds

```text
               ┌───────────────────────┐
               │   /cogitors <task>    │
               └───────────┬───────────┘
Round 1: Initial Analysis  ▼
────────────────────────────────────────────────────────
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    Codex    │   │ Antigravity │   │   Claude    │
  └─────────────┘   └─────────────┘   └─────────────┘
───────────────────────────┬────────────────────────────
                           ▼
               ┌───────────────────────┐
               │    Drafts Unsealed    │
               └───────────┬───────────┘
Round 2: Reconsideration   ▼
────────────────────────────────────────────────────────
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    Codex    │   │ Antigravity │   │   Claude    │
  └─────────────┘   └─────────────┘   └─────────────┘
───────────────────────────┬────────────────────────────
Round 3: Debate            ▼
────────────────────────────────────────────────────────
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    Codex    │─x─│ Antigravity │─x─│   Claude    │
  └─────────────┘   └─────────────┘   └─────────────┘
───────────────────────────┬────────────────────────────
Round 4: Final Position    ▼
────────────────────────────────────────────────────────
  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  │    Codex    │   │ Antigravity │   │   Claude    │
  └─────────────┘   └─────────────┘   └─────────────┘
───────────────────────────┐
Round 5: Synthesis         ▼
────────────────────┬──────────────┐
                    │    Elder     │
                    └──────────────┘
```

1. **Initial Analysis:** Each agent examines the task alone, without seeing the others.
2. **Reconsideration:** Agents read each other's drafts and may update their views.
3. **Debate:** Each agent defends its view with evidence and objects where it disagrees.
4. **Final Position:** Objections are answered and each agent sets its final stance.
5. **Synthesis:** The Elder gathers agreements, minority views and uncertainties into one decision.

---

## Decision Outputs and Directory Layout

Every session is saved in the task's language under your project's `docs/cogitors-decisions/` directory:

```text
<project-root>
  docs/cogitors-decisions/<time-stamp>-<slug>/
  ├── antigravity-<slug>.md
  ├── brief-<slug>.md
  ├── claude-<slug>.md
  ├── codex-<slug>.md
  ├── decision-<slug>.md
  └── decisions-<slug>.html
```

---

## Quick Install

Run `npx skills add erayendes/cogitors` and install all four skills. Details [here](docs/installation.md).

---

## Limits, Cost and Safety

- **Cost:** A session makes 8 external model calls (plus any timeout retries you approve), and you approve the scope before any call starts.
- **Source code:** Deliberation never edits code; if a source file changes, the session stops.
- **Participation:** If an agent fails, you are asked; a session never continues with fewer than 2 participants.
- **Time:** 180 seconds per call and 1800 seconds per session (`--timeout`, `--total-timeout`).

## The Story Behind the Name

**Cogitors** are ancient minds in the Dune universe that left their bodies behind and, preserved in a protective fluid, **devote thousands of years to thought**.
They reach a conclusion only after thinking and debating at length, never in haste.
This project takes its name from them: several models think through the same question without haste, questioning themselves and each other.

---

[Report a bug](https://github.com/erayendes/cogitors/issues/new?template=bug_report.yml) · [Request a feature](https://github.com/erayendes/cogitors/issues/new?template=feature_request.yml) · [Support](.github/SUPPORT.md) · [Security](.github/SECURITY.md) · [Contributing](.github/CONTRIBUTING.md) | [MIT](LICENSE) © [Eray Endes](https://github.com/erayendes)
