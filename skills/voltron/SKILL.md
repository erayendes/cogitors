---
name: voltron
description: Use when the user invokes /voltron or explicitly asks to form Voltron to build parts in parallel and join them. When a job clearly splits into two or more independent parts with separate files and checkable deliverables, propose forming Voltron and ask first. For one task seen from several views use lions. For a deliberation use cogitors.
---

# Voltron

Voltron is **formed**, the way the lions join into one robot: in every status line and summary the verb is *form* (Turkish *oluşturmak*: "Voltron oluşturuyoruz", "Voltron oluşturuldu"). The Elder splits the job at hand into parts, each lion builds one part at the same time, and the Elder joins the parts into one working whole. Read [lions](references/lions.md) first, for who the lions are, choosing models, the plan format, running and reading results; in a repository checkout it is `../cogitors/references/lions.md`.

## Form Voltron

1. **Split.** Read quota before planning. Break the current job into independent parts, one per lion, at most five. Give each part its own `owns` paths and a handoff contract: the named outputs the lion returns and the checks that prove the part done, each with the command to run. Write checks specific to the task, not roles ("be a careful developer"). State what does not count as done: a partial solution, a fix for a special case only, a reduction to another unverified claim, or a best-attempt summary. Tell a lion not to stop early only together with such a check as its gate. When parts meet at an interface, make sure the shared scaffold is in the working tree before dispatch. Every lion starts from the working tree as it is.
2. **Match lions to parts.** Choose each lion's tier or explicit model and effort by what its part demands. Use quota to rule out exhausted lions and break ties among capable lions.
3. **Announce.** Start right away on an explicit `/voltron` or request to form Voltron. If you proposed it, wait for the user's yes to the plan, including the lions, accounts, access and call ceiling. Say "Let's form Voltron!" in the user's language (Turkish "Voltron oluşturuyoruz!"). Show each lion's part and paths, and its dispatch line.
4. **Run** a `parts` plan with `--access edit`, or `review` when every part only reads (for example a review split by area).
5. **Join.** Start joining a part only when its named outputs and checks are back. Handle definite quota errors as described in the shared reference. A finding blocks a part only when evidence (a failing test or command, a counterexample, a reproducible error) shows it breaks the part's checks or contract; log the rest as non-blocking. Use diffs from successful lions with changes and get approval for any `outside_owns` change. Apply the diffs one by one, resolve conflicts, then run the project's own checks and fix what the joining broke. This step is done when every part is applied or set aside with a reason and the checks pass, or their failures are named.
6. **Report** to the user in their language: what each lion built, what you changed while joining, the check results, and any part left undone. Agreement among lions of one model family is not verification; for a result that matters, at least one check comes from another family or a machine-checkable step. Then clean the run.
