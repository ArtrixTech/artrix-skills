# AGENTS.md

Work toward a verifiable goal: establish the facts, choose the simplest sufficient approach, act, and use evidence to check the result and revise your judgment.

Apply the methods that fit the task, its risks, and its evidence gaps. Routine information lookup needs source verification; implementation needs behavior verification. Independent review and ablation have specific triggers in Section 3. These rules do not require every task to run every method or produce a separate report for every step.

## 1. Problem and Judgment

### Goal-Driven Execution

- Define the requested outcome, scope, constraints, and observable completion criteria before consequential action.
- Turn broad requests into checkable goals. For multi-step work, state a brief sequence with a verification check for each meaningful step.
- At milestones, handoffs, or context recovery in long tasks, recheck the original goal. Preserve established facts, key assumptions, remaining checks, and the next action so intermediate work does not replace the task itself.

### First Principles and Evidence

- Check the premise against primary evidence: the actual project state, source material, logs, measurements, or observed behavior. Establish what needs changing before choosing a fix.
- For a reported fault, identify the trigger, expected behavior, and observed behavior; establish a reproduction or the strongest available baseline before editing. Separate the symptom from the suspected cause. If reproduction is unavailable, preserve the evidence and label causal claims as hypotheses.
- For a feature, define the desired behavior and constraints. For information lookup, define the question and identify sources that can answer it. Neither task requires inventing a fault to reproduce.
- Distinguish observations, hypotheses, and recommendations. For a consequential causal claim or uncertain design assumption, identify what evidence would change your judgment.
- Verify APIs, signatures, flags, and behavior in the source or documentation before relying on them; check whether the information is current for the relevant version.

### Critical Judgment and Uncertainty

- Apply the same evidence standard to your own conclusions, the user's claims, and other agents' answers. Challenge weak reasoning and expose tradeoffs; revise your conclusion when the evidence changes.
- Investigate questions that available sources or tools can resolve before asking the user. For low-impact, reversible choices, state material assumptions and proceed.
- Ask when unresolved ambiguity changes the goal, scope, authorization, or a consequential outcome. Explain the decision at stake and continue independent work while waiting.

## 2. Design and Changes

### Simplicity First — Occam's Razor

Choose the simplest complete solution that meets the actual requirements, constraints, and reliability needs.

- Start with a working path small enough to validate. A script is sufficient when it solves the task; evolve the architecture when real requirements justify it.
- Keep features, flexibility, configuration, and defensive mechanisms tied to a stated requirement or a credible failure mode.
- Reduce duplication and unnecessary mechanisms. Judge simplicity by the cost of understanding, maintaining, and changing the solution, rather than line count alone.
- Introduce an abstraction when it clarifies ownership, isolates change, or serves an actual reuse need. Keep direct code when a new abstraction would only add indirection.

### Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### Architecture: Cohesion and Coupling

When adding or changing a module boundary, keep logic that changes together in one place. Define each component's responsibility, owned state, public interface, and dependencies so a local change can be understood and verified locally.

A system has three layers of structure that must stay aligned:

| Layer | What it answers |
|---|---|
| **Logical** | What are the conceptual components? What does each one own? |
| **Implementation** | How are those components realized in code — modules, classes, interfaces, data flow? |
| **File organization** | How are files and directories laid out on disk? |

#### Three-Layer Alignment

- Each logical component maps to a clear implementation boundary (module, class, service — whatever the stack uses).
- Each implementation boundary maps to a predictable file location.
- If you change one layer, verify the other two still match.

Smell test: can someone unfamiliar with the codebase locate a logical component and understand its ownership from the structure? Scattered ownership or misleading directories warrant investigation. Structural changes still follow the task scope and the surgical-change rules above.

#### One-Sentence Rule

Describe each logical component, module, and directory in one sentence: what it owns and what it does not. If the sentence is unclear, revisit the responsibility and boundary before extending it.

#### Place Before Create

Before adding a new file or directory, answer: "Which logical component does this belong to, and where does that component live?" If no boundary fits:
1. The structure may need adjustment, or
2. The new thing is poorly defined.

Never create a file with the intent to "figure out where it goes later."

#### Dependency Direction

Keep source dependencies between components directional and interfaces explicit. If a change introduces a dependency cycle, examine the ownership and remove the cycle within the affected scope. Distinguish source dependencies from legitimate two-way runtime communication.

#### Architecture.md

Each project maintains an `Architecture.md` at root — a living map of the current structure, not a design document.

Format:
```markdown
# Architecture

## Components
<list of logical components, each with a one-sentence description and its file-level location>

## Key Relationships (optional)
<brief prose on dependency/containment/data-flow between components, only when the component list alone is ambiguous>
```

Rules:
- Update when structure changes (component added/removed/split/merged, directory moved). Not for implementation-detail changes.
- Each entry connects the logical role to its physical location — don't describe one without the other.
- Keep it factual (what *is*), not aspirational (what *should be*).

## 3. Execution and Verification

### Work by Dependencies

- Run dependent operations in order; use intermediate results to choose the next action.
- Batch independent operations in one pass, not one at a time.
- Fan out independent subtasks to parallel subagents when you own the overall flow and the work is genuinely parallel.

### Match Verification to the Claim

Choose checks that directly support the requested outcome and cover the changed behavior. Scale verification to the failure cost, affected scope, and remaining uncertainty.

| Task | Useful verification |
|---|---|
| Information lookup | Check source authority, relevance, and currency; reconcile material contradictions. |
| Feature or input validation | Exercise the requested behavior and relevant failure cases. |
| Bug fix | Compare the same reproduction or observed scenario before and after; check the affected regression paths. |
| Refactor | Check observable behavior and interface compatibility before and after; passing existing tests alone may not establish equivalence. |
| Simple wording or formatting change | Inspect the changed content and its rendering when relevant. |

Use logs, measurements, device observations, minimal examples, or automated tests as appropriate. A test suite is one source of evidence, not a mandatory first step for every task. When a check fails, revisit the hypothesis or implementation; when evidence is unavailable, report the limit instead of treating the check as passed.

### Independent Judgment and Adversarial Review

Use independent review before finalizing substantial behavior changes, changes to shared interfaces or module boundaries, or important design decisions. Routine lookup, translation, formatting, and trivial mechanical edits do not trigger it; an explicit review request does.

- Use a reviewer who did not implement the change. Provide the goal, constraints, artifact, and primary evidence. Have the reviewer form an initial assessment before reading the implementer's conclusions or other reviewers' verdicts.
- Ask for counterexamples, omissions, regressions, and failure scenarios. Each finding must identify a trigger, an artifact location, supporting evidence, and its consequence. Reporting no findings is valid.
- Check findings against the evidence and resolve material issues before claiming completion. Recheck the affected behavior after a fix. Agreement among agents is not proof, and disagreement is a reason to investigate rather than vote.
- When several agents independently assess the same question, collect their initial conclusions and reasons before comparing them. Ordinary implementation handoffs may share context freely.
- If an independent reviewer is unavailable, state the limitation and perform the available checks without presenting self-review as independent validation.

### Ablation for Contribution Questions

Use ablation when a decision depends on the contribution of a component, rule, tool, or prompt segment and a meaningful controlled comparison is possible. Routine lookup, a straightforward logic fix, and ordinary regression verification do not require ablation.

- State the hypothesis, baseline, and decision-relevant metric before the experiment. In an isolated test or replay, remove or replace one factor while keeping inputs, environment, and other conditions as consistent as possible.
- Account for random variation with necessary repeat runs. If factors interact or conditions cannot be controlled, state the resulting attribution limit.
- Use the comparison to decide whether to retain, simplify, or remove the factor. Limit conclusions to the tested conditions: no observed difference does not establish universal uselessness.

## 4. Delivery and Recalibration

- Compare the delivered result with the original goal and completion criteria. Distinguish completed work from partial progress.
- Back claims such as "works", "tested", and "fixed" with relevant evidence: a command and result, test outcome, measurement, screenshot, or source location. Keep the claim within what that evidence establishes.
- Surface evidence gaps, untested scenarios, and assumptions that materially affect the conclusion or its use. Explain their impact and the next useful check when needed; simple answers need no routine uncertainty checklist.
- Be concise. No flattery or filler. Never open with "you are right". State what matters for the user's next decision.

## 5. Git & Commits

### Commit Style

- Use **Gitflow** branch naming and workflow conventions.
- Commit messages in **English**.
- Format: `<type>(<scope>): <subject>` (e.g., `feat(auth): add JWT refresh token rotation`).
- Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `ci`.
- Subject line: imperative mood, no period, ≤72 chars.
- Body (optional): explain *why*, not *what*. Wrap at 72 chars.

### Commit Discipline

- Make atomic commits after each conversation turn that produces changes.
- Unless the user explicitly requests otherwise, commit on the current branch — do not create sub-branches.
- Each commit should be self-contained and the repo should remain in a buildable/runnable state after every commit.

## 6. Documentation

### devlog.md (`docs/devlog.md`)

A running development log organized in reverse-chronological blocks.

Each block represents one commit:

```markdown
## <commit title>

`<commit hash>` | <date>

- **Changes**: <what was modified, compressed>
- **Reason**: <why>
- **User feedback**: <original user request/feedback, if any>
- **Process**: <experiments, tests, iterations — if any>
- **Result**: <outcome, effect, status>
- **Notes**: <anything useful for future tracing/debugging>
```

Rules:
- One block per commit. Add the commit hash after committing (the devlog update rides with the next commit — no dedicated commit needed).
- Keep text compressed but information-complete.
- Record anything that might aid future tracing or debugging.

### Precipitation Docs (`docs/precipitation/<YYMMDD>_<brief_name>.md`)

Long-lived knowledge artifacts: reflections, lessons learned, pitfalls, reusable workflows (debugging, migration, etc.), methodology.

Decision criterion: write a precipitation doc when the content is **durable and transferable** — valuable beyond the immediate task.

File format:
```markdown
# <Title>

## Summary
<1-3 sentence overview of what this document covers and why it exists>

## Content
<detailed content>
```

Naming rules:
- `YYMMDD` date prefix for chronological sorting.
- `brief_name` uses accurate keywords for future recall (e.g., `250713_playwright_flaky_test_strategy.md`).

---

## Meta: Self-Reference Notice

> **This section applies ONLY within this repository (`artrix-skills`).**
>
> This `AGENTS.md` is the canonical, continuously-iterated master copy. It is designed to be copied into other projects verbatim. **When copying to another project, remove this entire "Meta: Self-Reference Notice" section**, as the self-referential context only makes sense in this repo.
>
> In this repo, `AGENTS.md` itself is a managed asset — changes to it are tracked in `docs/devlog.md` like any other file.
