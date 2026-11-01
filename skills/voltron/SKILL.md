---
name: voltron
description: Use when the user invokes /voltron or explicitly asks to form Voltron: split the current job into parts that every other model and account builds at once, then join them. For one task seen from several views use lions; for a deliberation use cogitors.
---

# Voltron

Voltron is **formed**, the way the lions join into one robot: in every status line and summary the verb is *form* (Turkish *oluşturmak*: "Voltron oluşturuyoruz", "Voltron oluşturuldu"). The Elder splits the job at hand into parts, each lion builds one part at the same time, and the Elder joins the parts into one working whole. Read [lions](references/lions.md) first, for who the lions are, choosing models, the plan format, running and reading results; in a repository checkout it is `../cogitors/references/lions.md`.

## Form Voltron

1. **Split.** Break the current job into independent parts, one per lion, at most five; a small job uses fewer lions. Give each part its own `owns` paths so no two lions change the same file. When parts meet at an interface, write that shared scaffold yourself first (types, interfaces, stubs, the data contract) in the working tree; every lion starts from the working tree as it is.
2. **Match lions to parts.** Choose each lion's model and effort from `cogitor.py models` by what its part demands.
3. **Announce.** Say "Let's form Voltron!" in the user's language (Turkish: "Voltron oluşturuyoruz!"), then the plan: lion · model · effort → part (paths). Start right away unless the user asked to see the plan first.
4. **Run** a `parts` plan with `--access edit`, or `review` when every part only reads (for example a review split by area).
5. **Join.** Skip lions whose `status` is not `success` or whose `changed` is false, and decide what to keep of any `outside_owns` change. Apply the diffs one by one, resolve conflicts, then run the project's own checks and fix what the joining broke. This step is done when every part is applied or set aside with a reason and the checks pass, or their failures are named.
6. **Report** to the user in their language: what each lion built, what you changed while joining, the check results, and any part left undone. Then clean the run.
