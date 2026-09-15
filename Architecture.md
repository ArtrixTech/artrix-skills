# Architecture

## Components

| Component | Role | Location |
|---|---|---|
| Agent Guidelines | Canonical coding/workflow rules — the master copy iterated here and portable to other projects | `AGENTS.md` |
| Structural Map | Living description of this repo's architecture | `Architecture.md` |
| Development Log | Reverse-chronological commit-level changelog | `docs/devlog.md` |
| Precipitation Docs | Durable knowledge artifacts: lessons, pitfalls, reusable workflows | `docs/precipitation/` |
| Farm Rebuilder | Rebuilds the `~/.agents/skills` symlink farm from both skills repos; links every dir containing `SKILL.md` (root level and one group level deep), prunes stale links | `skills-link.sh` |
| Root Skills | Standalone, harness-agnostic skills | `agent-reach/`, `code-review/`, `find-skills/`, `human-writing/`, `impeccable/`, `kami/`, `meeting-minutes/`, `minimax-pdf/`, `mijia-label-printer/`, `paper-lookup/`, `research/`, `resolving-merge-conflicts/`, `seedance-25/`, `setup-pre-commit/`, `wizard/` |
| Matt Pocock Collection | The vendor-coupled engineering-skills set (tracker workflow, grilling, deep modules, writing series) — grouped, mutually referencing | `matt/` |
| Plannotator Wrappers | Skills bound to the plannotator CLI — annotation UI wrappers | `plannotator/` |
| Travel Skills | Travel data skill set (48 skills: flight/hotel comparison orchestrators, cash/award data sources, points knowledge bases) vendored from borski/travel-hacking-toolkit, with shared `data/` and `scripts/` | `travel-skills/` |