---
name: lions
description: Use when the user invokes /lions or asks every other model and account to do the same task separately, each from its own view. Also weigh it on every incoming task: when a mistake would be costly (security, payments, data migration, pre-release, a large or risky change), propose sending lions with a one-line reason and the lion plan, and ask first; never start it unasked. For splitting a job into parts use voltron. For a deliberation use cogitors.
---

# Lions

The lions set out separately: every lion does the same whole task from its own view, and the Black Lion compares what they bring back and gives the user one answer. Read [lions](references/lions.md) first, for who the lions are, choosing models, the plan format, running and reading results; in a repository checkout it is `../cogitors/references/lions.md`.

## Send the lions

1. **Write the task.** Read quota before planning. Give the `same` plan the user's task in their words, the scope and the expected output (for a review, findings with `file:line`, severity and evidence). Name the task's own checks with the commands to run, and state what does not count as done: a partial answer, a special case only, a reduction to another unverified claim, or a best-attempt summary. Ask a lion to keep going only together with such a check as its gate.
2. **Choose lions and models.** Cover as many independent families as quota allows. Pick the CLI or account by quota first, using capability only to rule out lions that cannot do the task. Then choose its model and effort from the live list for the task's size and risk. Follow any ordered `routing` fallback list as described in the shared reference.
3. **Announce.** Show the Black Lion's estimated management share and remaining quota in the plan line, with any handoff for joining and verification. Start on an explicit request. For a proposal, log the user's answer with `cogitor.py proposal --kind lions --answer ANSWER` and start only after a yes to the lions, accounts, access and call ceiling. Show access and each lion's dispatch line.
4. **Run** the `same` plan with `--access review`, or `edit` when each lion should produce its own version of a change to compare.

## Answer

Give the user one answer in their language. Follow the plan's assignment for joining and verification. Name the families that returned views and report any shortfall, for example "2 views instead of 3." Count accounts of the same CLI as one family. Merge duplicate findings and count how many families raised each one. Verify each finding, label it unconfirmed or drop it with the reason. A reviewer always finds something: a finding blocks only when evidence (a failing test or command, a counterexample, a reproducible error) shows it breaks the task's success criteria, a contract check or the checklist; report the rest as non-blocking. Agreement within one model family is not proof; for a conclusion that matters, at least one check comes from another family or a machine-checkable step. Show raw reports only when the user asks. For `edit`, compare the lions' diffs and apply the best one, or combine them. Then clean the run.
