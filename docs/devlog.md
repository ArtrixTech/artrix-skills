## docs(agents): silence routine upstream sync checks

`pending` | 2026-10-10

- **Changes**: Added a Conversation Start rule to run the upstream check silently and speak only when an update was applied, a user decision is needed, or the check failed; bumped AGENTS.md to V1.3.
- **Reason**: Downstream agents opened every conversation by announcing that rules matched upstream, which is noise.
- **User feedback**: 「下游的所有使用了这个文件的Agent，都在每一次对话的最开头提示规则与上游一致，无需同步……只在已经同步或者需要用户知道的时候才表述出来……但是原定的检查更新的工作依然需要做」
- **Process**: Fetched origin; local AGENTS.md matched origin/main before the edit. Kept the check steps and the unavailable-GitHub report unchanged.
- **Result**: The check still runs on the first turn; the "already current" outcome produces no message.
- **Notes**: Behavioral revision, so minor bump. Downstream copies pick this up only after it is pushed to GitHub.

## chore(skill): remove meeting-minutes

`a340bca` | 2026-10-10

- **Changes**: Deleted `meeting-minutes/` (SKILL.md plus agents/openai.yaml), dropped it from the Root Skills registration in `Architecture.md`, and removed the `~/.agents/skills/meeting-minutes` farm link.
- **Reason**: The user decided to retire the local meeting-minutes skill.
- **User feedback**: 「需要删掉本地的会议纪要skill，删除之前让我确认是哪个」 — scope confirmed as source directory plus symlink, with commit and push.
- **Process**: Scanned `~/.agents/skills`, `~/.pi/agent/skills`, `~/.claude/skills`, `~/.codex/skills`, and both skills repos by name and by `会议纪要` body text, finding one canonical directory and one farm link. Used `git rm -r`, then removed the git-untracked empty `references/` directory. Carried the pre-existing `skills-link.sh` mode bit and `travel/SKILL.md` description edit through untouched.
- **Result**: The repo and the farm hold no meeting-minutes entry; `git show` reports 50 deletions across three files. ArtrixClaw was 18 commits behind origin/main and its worktree never carried the skill, so the pull leaves it absent there as well.
- **Notes**: Devlog hash follows the next-commit convention. The remote farm needed no pruning.

## chore(impeccable): update canonical Codex skill to 4.3.1

`pending` | 2026-09-19

- **Changes**: Replace the untouched 3.9.1 vendor import with the official Codex 4.3.1 payload; include native iOS/Android guidance, new-work and craft references, specialist agent definitions, and the version-pinned engine launcher. Ignore downloaded platform binaries and register the runtime structure.
- **Reason**: The global updater skipped the canonical `~/.agents/skills/impeccable` symlink, leaving Codex on the older source while copied provider installs updated.
- **User feedback**: Approved updating Impeccable during the GolfDemo UI design task.
- **Process**: Confirmed canonical guidelines match GitHub and the skill has no edits since import. Installed the official Codex payload into a temporary project with hooks disabled; mirrored only the skill directory; verified payload hashes, symlink resolution, skill version, and engine handshake.
- **Result**: The existing skills-farm link now resolves to 4.3.1, with local darwin-arm64 engine 0.1.5. No GolfDemo files changed.
- **Notes**: Preserve unrelated untracked Python cache directories. No provider hooks or global Codex configuration changes. Commit hash follows the next-commit devlog convention.

## feat(travel-skills): vendor borski/travel-hacking-toolkit as grouped skill set

`3506b95` | 2026-09-15

- **Changes**: Vendored 48 travel skills plus shared `data/` and `scripts/` from borski/travel-hacking-toolkit @ 901675d into `travel-skills/`; added top-level README; registered the group in `Architecture.md`; rebuilt the farm so all 48 resolve through the repo.
- **Reason**: `npx skills add` had dumped 48 loose copies into `~/.agents/skills` outside the two-repo source of truth, invisible to farm rebuilds and ArtrixClaw sync.
- **User feedback**: 「帮我做成travel-skills文件夹，顶层写一个介绍」
- **Process**: Confirmed group-dir convention from `matt/` and `plannotator/`; copied skills+data+scripts; wrote README; ran `skills-link.sh --replace`; verified 48/48 symlinks.
- **Result**: 48 travel skills live in the public repo with data and update procedure documented; farm count 99 links.
- **Notes**: Upstream sync steps are in `travel-skills/README.md`; `~/GitHub/travel-hacking-toolkit` clone kept for `git pull` diffs.

## fix(skill): default meeting minutes to prose and ask about cards

`43406bfd0c8fa22baee027303d60f22d9bb7ec93` | 2026-09-13

- **Changes**: Make prose the explicit default for both summaries and owner actions; ask once about an optional card when the preference is unknown, with text-only as the default.
- **Reason**: Match the user's writing preference and avoid inferring a card request from visual suitability.
- **User feedback**: “非必要不用bulletpoint需要引入。需要主动询问是否需要卡片，默认不需要。”
- **Process**: Checked unspecified, explicitly requested, declined and existing-card revision branches; ran the skill validator and whitespace check.
- **Result**: Unanswered card questions leave text delivery unblocked; existing explicit choices persist; lists remain available where they materially aid comprehension.
- **Notes**: Preserved unrelated cache directories and carried forward the prior commit hash under the devlog convention.

## feat(skill): add general meeting minutes workflow

`8fe9ff26ae8e55c12d4835e461e3765b147f5b44` | 2026-09-13

- **Changes**: Add meeting-minutes with a concise evidence-to-minutes workflow, a conditional visual-card reference, implicit invocation policy, and Architecture registration.
- **Reason**: Reuse the meeting-summary and detailed-card workflow across teams and subjects while leaving archive conventions to each repository.
- **User feedback**: “总结当前的工作流然后收敛成一个skill”; “作为通用的会议纪要完成，不止适用于刘杨的会议”; “放在artrix-skills里面”.
- **Process**: Skill validator passed. An independent community-reading-meeting exercise retained conflicting attendance, unaccepted ownership, undecided fees and source-command boundaries without invoking image or web tools. Installed and verified the new skill's local discovery symlink.
- **Result**: Paragraph summaries, attributable actions, optional information-rich cards, semantic image checks and persistent delivery share one reusable entrypoint; no LY-specific people, topic or directory paths embedded.
- **Notes**: Existing previous-commit hash update carried forward under the devlog convention; unrelated cache directories preserved. Local commits only.

## feat(skill): sync standalone Mijia BLE printer skill

`5af15f5` | 2026-09-11

- **Changes**: Add mijia-label-printer runtime skill (SKILL.md, agents, scripts, references), register its Architecture location.
- **Reason**: User requested GitHub publication of a standalone printer skill and synchronization into artrix-skills.
- **Process**: Runtime mirrored from ArtrixTech/mijia-label-printer at e2e24ce; seven captured-frame/fake-transport tests and independent offline review pass, skill validator passes; byte equality checked before publication.
- **Result**: Explicit scan/status/render/print commands, chosen device ID, short-label bounds, TLV status and buffer checks, unique evidence directories. Original “你好世界” print physically confirmed; packaged new idle monitoring remains simulated because device was no longer discoverable.
- **Notes**: Canonical implementation: https://github.com/ArtrixTech/mijia-label-printer . Existing unrelated human-writing __pycache__ preserved.

# Development Log

<!-- Reverse-chronological. Latest block on top. -->

## feat(skill): add Cursor conversation recall

`57bb6a3` | 2026-09-27

- **Changes**: Add `cursor-conversations` with a standard-library reader script (`list`, `search`, `find`, `read`, `stats`) and a SKILL.md documenting the on-disk layout, JSONL record format, index truncation limits, and read order; register it in `Architecture.md`.
- **Reason**: Cursor keeps full agent transcripts locally, and reading them by hand loses the structure that makes a long conversation usable; the skill makes recall repeatable and keeps it behind an explicit request.
- **User feedback**: “方法论写成skill放到~/GitHub/artrix-skills里面，只在用户显式要求读取cursor对话时使用。另外提供让agent完整读取对话的方式/指导。”
- **Process**: Inspected 291 transcripts across 53 workspaces plus the FTS index, and confirmed three index limits by measurement: body capped at 10 KB per conversation against a 233 KB transcript, tool names and arguments absent from the body, and asynchronous re-indexing. Verified all five subcommands against a real conversation, including skeleton and tail rendering and both heredoc extractions quoted in SKILL.md.
- **Result**: One command surface covers discovery through full reading; explicit-invocation policy set in both SKILL.md frontmatter and `agents/openai.yaml`.
- **Notes**: Paths and format are Cursor internals without a stability guarantee; SKILL.md says to re-inspect a live transcript when shapes drift. Commit hash follows the next-commit devlog convention.

## fix(skill): default to publishable meeting cards and prose

`f4959b2` | 2026-09-20

- **Changes**: Make meeting cards the default deliverable; fold the visual-card guidance into the main skill, remove the standalone reference, set the default card ratio to 2:3, and require publishable outputs without internal transcript locations or tool traces.
- **Reason**: Align the reusable workflow with the current meeting-delivery standard and the updated card expectations.
- **User feedback**: “默认生成卡片”; “卡片风格需要直接移动到主skill文件里面来”; “输出的内容需要完全是对外可直接发布的状态”.
- **Process**: Rewrote the skill, removed the obsolete reference, cleaned the current LY minutes of internal citations, and ran the skill validator plus symlink and content checks.
- **Result**: The skill now produces a text summary and 2:3 alignment card by default, while allowing an explicit opt-out; the current golf minutes are publishable prose with business uncertainty preserved.
- **Notes**: Preserve unrelated cache directories. Commit hash follows the documented next-commit convention.

## docs(devlog): record AGENTS synchronization changes

`this commit` | 2026-09-08

- **Changes**: Commit the deferred upstream-sync policy log and record the V1.2 commit hash.
- **Reason**: Complete the history while preserving the AGENTS.md-only policy commit.
- **User feedback**: "提交".
- **Process**: Reviewed the remaining diff and checked whitespace.
- **Result**: Development log caught up with the committed rules; publishing remains pending.
- **Notes**: Previous entry: `a021ad1`.

## docs(agents): add upstream sync and repository-specific rules

`a021ad1` | 2026-09-08

- **Changes**: Added first-turn GitHub checks, SHA-based comparison, confirmation for private edits, and dedicated single-file sync commits with a devlog exemption. Added Repo-Specific Rules and moved master-only guidance there. Updated the Chinese comparison; V1.2 unchanged.
- **Reason**: Keep distributed copies current while preserving local overrides and unpublished master revisions.
- **User feedback**: First-message update checks, private-change merge confirmation, default append to repo-specific rules, single-file commits; "不用更新版本号".
- **Process**: Verified the public GitHub main/file URLs; independent review caught and resolved baseline refresh after approved merges. Checked shared-section preservation and full Chinese coverage.
- **Result**: Sync policy and private-rule boundary added; publishing to GitHub remains pending.
- **Notes**: Previous entry: `cf2b2f4`. This authoring change was committed as AGENTS.md only per user request; this log entry is included in the following log commit.

## docs(agents): establish V1.2 and versioning rules

`cf2b2f4` | 2026-09-08

- **Changes**: Set the AGENTS.md title to V1.2. Added master-copy versioning in Meta: minor for behavioral revisions, major/reset minor for incompatible policy changes, no bump for editorial-only edits. Synced the Chinese comparison.
- **Reason**: Track methodology revisions without applying this version policy to downstream project code.
- **User feedback**: "增加版本号逻辑，当前版本V1.2".
- **Process**: Checked the scoped diff, current version, and Chinese source-line coverage.
- **Result**: V1.2 established as the current document version.
- **Notes**: Previous entry: `5bca937`.

## docs(agents): distill methodology to core intents

`5bca937` | 2026-09-08

- **Changes**: Replaced procedural teaching, verification tables, and repeated caveats with concise principles and essential triggers. Kept one routine-lookup exemption and retained Git, Documentation, Meta, and Architecture.md policies. Updated the separate Chinese full-text comparison.
- **Reason**: Let clear intent and familiar principles guide agents without prescribing routine execution details.
- **User feedback**: "不是文字层面的浓缩，是意图明确层面的浓缩"; "原则本身就已经足够Agent理解".
- **Process**: Independent intent and translation checks; restored the root-cause requirement identified by review. Verified complete Chinese coverage, policy preservation, and responsive expand/collapse and keyboard behavior.
- **Result**: Methodology reduced from 1668 to 382 English words; full document from 231 to 125 lines.
- **Notes**: Previous entry: `cfcc6a8`. Chinese display remains outside the repository.

## docs(agents): unify goal-driven methodology and verification

`cfcc6a8` | 2026-09-08

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

## feat(travel): add travel entry skill, hide sub-skills from model

`a2c60b2` | 2026-09-30

- **Changes**: 新增 `travel/` 总入口 skill（48 项子技能索引，按 category 分组，描述 721 chars）；46 个 `travel-skills/*/SKILL.md` 加 `disable-model-invocation: true`（plan-trip、getting-started 原有）；Architecture.md 增补 Travel Entry 组件行。
- **Reason**: 每个新会话系统提示词 skills section 46,129 chars，旅行包独占 17,375；隐藏子技能 + 常驻入口后投影降至 ~28.5k，子技能按需读取。
- **User feedback**: 一期方案——做成总旅游入口 skill，有需要再读取列表，入口 skill 保持在上下文。
- **Process**: 确认 farm（~/.agents/skills）被 pi 直接扫描（paseo 无 ~/.pi/agent/skills 软链仍进提示词，bundle 含 ".agents" 扫描证据）；dry-run 模拟 pi 过滤器：隐藏 52 + 新增 1 后 farm 可见集 31，加包内 25 = 56，与 107-52+1 吻合，零遗漏。
- **Result**: travel 入口可见、46+2 个旅行子技能全部退出自动路由；paseo 6 个（仓外本地目录，本期一并处理）同加开关，备份 ~/.pi/agent/backups/paseo-skills-20260930-161034.tar.gz（不入本仓）。
- **Notes**: 新增旅行子技能后需在 travel/SKILL.md 索引补行；子技能两条手动路径均可用：/skill:<name> 与直接 read ~/.agents/skills/<name>/SKILL.md。
