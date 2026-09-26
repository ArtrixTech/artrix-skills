---
name: cursor-conversations
description: Read and search Cursor agent conversations stored on this machine. Use when the user explicitly asks to read, search, recover, or continue a Cursor chat/agent conversation, or supplies a Cursor conversation (agent) id. Only invoke on an explicit request.
disable-model-invocation: true
---

# Cursor Conversations

Cursor writes every agent conversation to disk in full. This skill reads those files directly, so the full record is available offline: user messages verbatim, assistant prose, every tool invocation with its arguments, attached images, subagent transcripts, and the error that ended each turn.

Invoke only when the user asks for it. Reading someone's chat history on a hunch is a privacy decision, not a retrieval optimization.

## 1. What is on disk

Everything lives under `~/.cursor`, with one SQLite index in `~/Library/Application Support/Cursor/`.

### Full transcripts (authoritative)

```
~/.cursor/projects/<workspace-slug>/agent-transcripts/<conversation-id>/<conversation-id>.jsonl
```

- `<workspace-slug>` is the absolute workspace path with `/` replaced by `-`, leading slash dropped: `/Users/artrix/GitHub/repo` becomes `Users-artrix-GitHub-repo`.
- One JSONL record per turn, appended as the conversation runs. A conversation still open on screen has a file that grows.
- Conversation ids are UUIDs. The user may hand over the id, or only the directory name shown in the Cursor UI; the id is also the parent directory name, so either resolves.

Sibling material inside the same transcript directory:

| Path | Content |
|---|---|
| `subagents/<uuid>.jsonl` | Subagent conversations the parent spawned, same record format |
| `../../assets/` | Images the user attached, referenced from user messages by absolute path |
| `../../terminals/<id>.txt` | Captured terminal output referenced by `<system_notification>` blocks |
| `../../mcps/<server>/` | MCP tool working state (browser profiles, app control), no conversation text |

A workspace directory also carries `canvases/` (project-scoped canvas artifacts) and `agent-tools/` (usually empty).

### Search index (discovery only)

```
~/Library/Application Support/Cursor/User/globalStorage/conversation-search.db
```

SQLite with an FTS5 table. Two columns matter: `conversations(id, title, source, scope, updated_at, is_archived)` and `conversation_fts(title, body, branches)` joined on `conversations.fts_rowid = conversation_fts.rowid`.

Three limits decide how it may be used:

1. **The body is truncated.** Cursor caps the indexed body per conversation (10 KB by default, in `conversation_search_settings.effective_conversation_cap`), against transcripts that run to hundreds of kilobytes. The real conversation here indexes 8 KB of a 233 KB file.
2. **The body holds prose only.** Tool names and tool arguments are not indexed. A search for a file path that appears only inside a `Read` or `StrReplace` call returns nothing.
3. **It can lag.** `conversation_search_candidates` and `conversation_search_reconciliation` drive an asynchronous re-index, so the newest turns may be absent.

So: the index answers *which* conversation; the JSONL answers *what was said*.

## 2. Record format

Every line of a transcript is one JSON object. Three shapes appear.

**Dialogue turn** — `role` is `user` or `assistant`, `message.content` is a list of blocks:

```json
{"role": "assistant", "message": {"content": [
  {"type": "text", "text": "..."},
  {"type": "tool_use", "name": "Read", "input": {"path": "/abs/path.ts"}}
]}}
```

Block types worth knowing: `text` (prose; for assistant records this mixes final answer and internal reasoning), `tool_use` (`name` plus `input`). Tool *results* are not stored in this file — only the invocation. Terminal output arrives as a later user message wrapped in `<system_notification>`, pointing at a file under `terminals/`.

**User message envelope** — the human's words sit inside `<user_query>...</user_query>`, alongside `<timestamp>` and, for image turns, an `<image_files>` block listing saved attachment paths:

```json
{"role": "user", "message": {"content": [{"type": "text", "text":
  "[Image]\n<image_files>...</image_files>\n<timestamp>Saturday, Sep 26, 2026, 3:42 PM (UTC+8)</timestamp>\n<user_query>\n…\n</user_query>"}]}}
```

Some later user records are Cursor's own automation prompts (`Briefly inform the user about the task result…`) rather than anything the person typed. Read them as system noise.

**Turn terminator** — no `role`, carries the ending:

```json
{"type": "turn_ended", "status": "error", "error": "Connection failed repeatedly"}
```

`status: "error"` is how an interrupted conversation is identified. An aborted turn explains mid-task truncation, which matters when the transcript is being used to judge what still needs doing.

## 3. Reading a conversation

Use the bundled script. Standard library only, no dependencies.

```bash
S="$HOME/GitHub/artrix-skills/cursor-conversations/scripts/cursor_conversations.py"   # adjust to the clone path

python3 "$S" list --limit 20                 # newest conversations, all workspaces
python3 "$S" list --workspace mingde         # filter by workspace slug
python3 "$S" stats d4553e6f                  # size, turns, opening message, end status, subagents
python3 "$S" search "visual tension"         # FTS query against Cursor's index
python3 "$S" find "DigitalTwinHUD" -i        # regex grep across raw JSONL
python3 "$S" read d4553e6f --skeleton        # one line per turn: role, sizes, tool names
python3 "$S" read d4553e6f                   # full Markdown rendering
python3 "$S" read d4553e6f --tools           # include tool invocations
```

Ids accept an unambiguous prefix.

### Order of operations

1. **Locate.** Given an id, go straight to `stats`. Given only a topic, run `search`, and when the index misses, `find` — `find` reads every transcript and is the only search that sees tool arguments.
2. **Map before reading.** `read --skeleton` on anything above ~50 KB. It gives the whole arc in one screen and shows which turns are prose-heavy versus tool-heavy, so the actual reads can be targeted.
3. **Read, then verify against the repo.** The repository is the ground truth for what a conversation produced. Compare the last recorded tool calls — commit hashes, file writes, test runs — against `git log` and `git status` before repeating any of the work. An interrupted conversation leaves uncommitted changes and unverified edits behind, and the transcript will not say which.
4. **Attachments.** When a user message lists an image, read the file at that path. Screenshots carry the visual complaint that the text only half-describes.

### When shelling out by hand

For one-off extraction, the raw file is fine — the script does nothing the file does not support:

```bash
V=~/.cursor/projects/Users-artrix-GitHub-mingde-hand-display/agent-transcripts/d4553e6f-434c-45a3-8df4-aa46fd86bda7

# every human-written query, in order
python3 -c "
import json,sys,re
for line in open(sys.argv[1]):
    d=json.loads(line)
    if d.get('role')!='user': continue
    for b in d['message']['content']:
        if b.get('type')=='text':
            m=re.search(r'<user_query>\s*(.*?)</user_query>', b['text'], re.S)
            if m: print('---'); print(m.group(1).strip())
" "$V"/*.jsonl

# the final assistant answer only
python3 -c "
import json,sys
recs=[json.loads(l) for l in open(sys.argv[1])]
texts=[b['text'] for d in recs if d.get('role')=='assistant'
       for b in d['message']['content'] if b.get('type')=='text']
print(texts[-1])
" "$V"/*.jsonl
```

Skip `jq` for transcripts. Records carry long single-line tool arguments, and dumping them whole floods the context with strings that were never meant to be read.

## 4. Reporting what was read

The user is asking about their own past work, so lead with the substance and keep the mechanics out of the way.

- Quote the user's own words and the assistant's conclusions; paraphrase tool traces.
- Report the file path and id once, so the conversation can be reopened. Never paste tool arguments as a block of evidence.
- Mark anything that could not be verified (no transcript, unreadable attachment, index miss) rather than filling the gap.
- When the goal is to continue the work, end with what remains unverified or uncommitted, and offer next steps.

## 5. Boundaries

- **Read-only.** Never modify, delete, or relocate anything under `~/.cursor/`. The FTS index and the `.sync/index.sqlite` inside `AgentStores/` are live Cursor state; open them read-only, or not at all.
- **One machine's history.** These paths are local and macOS-specific. Conversations from Cursor web or another device leave no transcript here.
- **Not a substitute for the repo.** A conversation records intent and attempts. Only the working tree and Git history record what actually landed.
- **Cursor's own format.** `~/.cursor/projects` and the JSONL layout are Cursor internals without a stability guarantee. When the shapes stop matching this document, re-inspect a live transcript before trusting the parser.
