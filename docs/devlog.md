# Development Log

<!-- Reverse-chronological. Latest block on top. -->

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
