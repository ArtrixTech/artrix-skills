# Development Log

<!-- Reverse-chronological. Latest block on top. -->

## docs(agents): unify goal-driven methodology and verification

`this commit` | 2026-09-08

- **Changes**: Reorganized AGENTS.md into problem/judgment, design/changes, execution/verification, and delivery/recalibration, followed by the existing Git and documentation policies. Integrated first principles, critical and independent judgment, adversarial review, ablation, Occam's razor, material uncertainty, and cohesion/coupling with concrete triggers and completion evidence. Replaced blanket stop-and-ask, line-count, abstraction, and architecture-failure rules with scoped decisions; retained surgical changes and operational policies.
- **Reason**: Form one goal-driven methodology from the existing guidelines and the eight proposed principles, while keeping routine lookup and simple edits lightweight.
- **User feedback**: "完成改写，然后用一个简单可视化来让我看中文版（不影响文档英文）的整个md、哪些是新的（它们插入到了哪里）。"
- **Process**: Independent review of the English rules and a separate review of the full Chinese comparison. Confirmed unchanged Git/Documentation/Meta policies, English-only master text, coverage of every nonblank source line, and all 29 visible line references. Browser checks passed at 736/360px in light and dark themes and 320px in light, including expand/collapse and keyboard interaction; fixed a long inline filename overflow. No runtime code changed.
- **Result**: English master updated to six sections; separate Chinese full-document visualization marks additions, rewrites, moves, and retained rules with original locations and current English line references.
- **Notes**: Previous devlog block ends at `4b074d7`. The Chinese visualization is outside the repository and does not create a second maintained AGENTS.md.

## refactor(skills): prune vendor-specific skills and group collections into folders

`422a5cc` + `4b074d7` | 2026-09-01

- **Changes**: Removed 28 skill dirs (arkcli-* ×25, git-guardrails-claude-code, claude-handoff, logo-generator); moved plannotator-* (3) into `plannotator/` and the Matt Pocock collection (29) into `matt/`. `skills-link.sh` upgraded: group-dir support (scans `<group>/<skill>/SKILL.md`) plus stale-link pruning for farm links pointing into the two repos. `Architecture.md` updated to the new layout.
- **Reason**: Repo is the shared cross-harness skill distribution channel (Mac pi + ArtrixClaw pi farms); harness/tool-specific skills were polluting it. Grouping keeps the plannotator and Matt Pocock sets intact (they cross-reference internally) while marking their boundaries.
- **User feedback**: "ark，ggcc，claude-handoff删掉。plannotator、matt，用文件夹放起来来收纳整理（确认一下这不会影响这些skills的正常读取）。logogenerator删掉。"
- **Process**: Verified the discovery surface is the flat `~/.agents/skills` farm (pi settings.json has no repo-path skill source; `~/.claude/skills` holds arkcli-managed copies outside this repo), so repo-side nesting cannot break reads: farm links stay flat one level. Rebuilt farm with `skills-link.sh --replace` and verified every link resolves to a frontmatter-valid SKILL.md.
- **Result**: Public skills 73 → 45 (13 root + 29 matt/ + 3 plannotator/); farm 78 → 48 links, all resolving. Private repo (3 skills) untouched.
- **Notes**: `~/.claude/skills` still holds arkcli-managed copies (its own connect channel, tracked by `.arkcli-managed-skills.json`) — separate distribution, cleanup pending owner decision. Remote ArtrixClaw farm to be rebuilt after it pulls this commit.


## docs: add architecture principles and Architecture.md

`560652b` | 2026-07-18

- **Changes**: Added Section 3 (Architecture) to `AGENTS.md` with three rules: one-sentence rule, place-before-create, dependency direction. Defined `Architecture.md` convention. Created `Architecture.md` for this repo. Renumbered sections 3→4, 4→5, 5→6, 6→7.
- **Reason**: User wants structural clarity enforced — every component/folder should have explainable boundaries and relationships.
- **User feedback**: "一个项目应该从头到尾清楚里面的每一个文件夹、每一个组件是干嘛的" — structure must be fully explainable, no redundancy or ambiguity.
- **Process**: Proposed three lightweight operational rules (not abstract principles) to keep mechanism low-overhead. Architecture.md positioned as living map (what *is*) not design doc (what *should be*). Avoided ADR-style heavyweight process since precipitation docs already cover decision rationale.
- **Result**: AGENTS.md now 7 sections. Architecture.md created for this repo.

## docs: add AGENTS.md and initialize devlog structure

`20999d9` | 2026-07-13

- **Changes**: Created `AGENTS.md` (master copy); initialized `docs/devlog.md` and `docs/precipitation/` directory.
- **Reason**: Bootstrap the repo's core agentic assets — a portable coding guidelines doc and project documentation structure.
- **User feedback**: User requested a unified AGENTS.md synthesizing Karpathy's coding guidelines with personal project management habits (gitflow commits, devlog, precipitation docs).
- **Process**: Merged Karpathy's 4 principles (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) with user's commit style, devlog format, precipitation doc convention, communication/behavior/action rules. Added self-reference meta section at bottom.
- **Result**: Complete AGENTS.md ready for iteration; docs structure in place.
