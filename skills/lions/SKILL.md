---
name: lions
description: Use when the user invokes /lions or explicitly asks every other model and account to do the same task separately, each from its own view (a code review, an analysis, a second opinion). For splitting a job into parts use voltron; for a deliberation use cogitors.
---

# Lions

The lions set out separately: every lion does the same whole task from its own view, and the Elder compares what they bring back and gives the user one answer. Read [lions](references/lions.md) first, for who the lions are, choosing models, the plan format, running and reading results; in a repository checkout it is `../cogitors/references/lions.md`.

## Send the lions

1. **Write the task** for a `same` plan: the user's task in their words, the scope, and the output you need back (for a review: findings with `file:line`, severity and evidence).
2. **Choose lions and models.** By default every available lion goes. Pick each one's model and effort from `cogitor.py models`; prefer different model families, since the point is independent views.
3. **Announce** the lions, models and access in one short block, then start right away unless the user asked to see the plan first.
4. **Run** the `same` plan with `--access review`, or `edit` when each lion should produce its own version of a change to compare.

## Answer

Give the user one answer in their language. Account for every finding: merged with its duplicates and counted by how many lions raised it (3/4), verified by you, labeled as unconfirmed, or dropped with the reason. Show raw reports only when the user asks. For `edit`, compare the lions' diffs and apply the best one, or combine them. Then clean the run.
