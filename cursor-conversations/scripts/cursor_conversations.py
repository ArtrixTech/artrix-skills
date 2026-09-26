#!/usr/bin/env python3
"""Read Cursor agent conversations from local disk.

Cursor keeps the full record of every agent conversation as JSONL under
~/.cursor/projects/<workspace-slug>/agent-transcripts/<id>/<id>.jsonl, and a
separate SQLite full-text index at
~/Library/Application Support/Cursor/User/globalStorage/conversation-search.db
whose per-conversation body is capped (10 KB by default), so it is useful for
discovery and useless for reading.

This script owns both halves: the index answers "which conversation", the JSONL
answers "what was actually said". Standard library only.

Subcommands:
    list      enumerate conversations, newest first
    search    full-text search titles and bodies via the SQLite index
    find      grep raw JSONL across transcripts when the index misses something
    read      render one conversation as readable Markdown
    stats     per-conversation size, turn count, and end status
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sqlite3
import sys
from typing import Any, Iterator

CURSOR_DIR = os.path.expanduser("~/.cursor")
PROJECTS_DIR = os.path.join(CURSOR_DIR, "projects")
INDEX_DB = os.path.expanduser(
    "~/Library/Application Support/Cursor/User/globalStorage/conversation-search.db"
)

# Transcript records that carry prose, in Cursor's own vocabulary.
TEXT_KEYS = ("text",)
TOOL_ARG_SUMMARY_KEYS = ("path", "file_path", "target_file", "command", "query", "pattern")


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #


def project_dirs() -> list[str]:
    """Every project directory holding agent transcripts, across all workspaces."""
    return sorted(glob.glob(os.path.join(PROJECTS_DIR, "*")))


def project_label(project_dir: str) -> str:
    """Turn a workspace slug such as ``Users-artrix-GitHub-repo`` into a path hint."""
    name = os.path.basename(project_dir.rstrip("/"))
    if name.startswith("Users-"):
        return "/" + name.replace("-", "/", 1).replace("-", "/")
    return name


def transcript_paths(workspace: str | None = None) -> Iterator[tuple[str, str, str]]:
    """Yield ``(conversation_id, project_dir, jsonl_path)`` for every transcript.

    ``workspace`` filters by substring match against the slug or the decoded path.
    """
    needle = workspace.lower() if workspace else None
    for project_dir in project_dirs():
        slug = os.path.basename(project_dir.rstrip("/"))
        haystack = f"{slug} {project_label(project_dir)}".lower()
        if needle and needle not in haystack:
            continue
        for path in glob.glob(
            os.path.join(project_dir, "agent-transcripts", "*", "*.jsonl")
        ):
            # Subagent transcripts live one level deeper and are excluded here.
            yield os.path.basename(path)[: -len(".jsonl")], project_dir, path


def find_transcript(conversation_id: str) -> tuple[str, str]:
    """Resolve a conversation id (or unambiguous prefix) to ``(project_dir, path)``."""
    matches = [
        (project_dir, path)
        for cid, project_dir, path in transcript_paths()
        if cid == conversation_id or cid.startswith(conversation_id)
    ]
    if not matches:
        raise SystemExit(f"no transcript for id {conversation_id!r}")
    if len(matches) > 1:
        listing = "\n".join(f"  {os.path.basename(p)}  {d}" for d, p in matches)
        raise SystemExit(f"ambiguous id {conversation_id!r}, matches:\n{listing}")
    return matches[0]


def subagent_paths(transcript: str) -> list[str]:
    """Subagent transcripts recorded beneath a parent conversation."""
    directory = os.path.join(os.path.dirname(transcript), "subagents")
    return sorted(glob.glob(os.path.join(directory, "*.jsonl")))


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #


def load_records(path: str) -> list[dict[str, Any]]:
    """Parse a transcript, skipping unparseable lines rather than failing."""
    records: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def content_blocks(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalise ``message.content`` to a list of blocks."""
    content = (record.get("message") or {}).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict)]
    return []


def block_text(block: dict[str, Any]) -> str:
    for key in TEXT_KEYS:
        value = block.get(key)
        if isinstance(value, str):
            return value
    return ""


def tool_summary(block: dict[str, Any]) -> str:
    """One-line human summary of a tool invocation."""
    name = block.get("name") or "tool"
    args = block.get("input") or block.get("arguments") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {"raw": args}
    if not isinstance(args, dict):
        return name
    for key in TOOL_ARG_SUMMARY_KEYS:
        value = args.get(key)
        if isinstance(value, str) and value:
            return f"{name}: {value}"
    return name


def strip_envelope(text: str) -> str:
    """Pull the human-written query out of Cursor's user-message envelope."""
    match = re.search(r"<user_query>\s*(.*?)\s*</user_query>", text, re.DOTALL)
    return match.group(1) if match else text


def iteration(records: list[dict[str, Any]]) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield ``(kind, record)`` where kind is user, assistant, or event."""
    for record in records:
        if record.get("type") == "turn_ended":
            yield "event", record
            continue
        role = record.get("role")
        if role in ("user", "assistant"):
            yield role, record
        elif role is None and record.get("type"):
            yield "event", record


# --------------------------------------------------------------------------- #
# Index access
# --------------------------------------------------------------------------- #


def index_rows(query: str, limit: int) -> list[dict[str, Any]]:
    """Query Cursor's own FTS index; returns [] when the index is absent."""
    if not os.path.exists(INDEX_DB):
        return []
    connection = sqlite3.connect(f"file:{INDEX_DB}?mode=ro", uri=True)
    try:
        sql = (
            "SELECT c.id, c.title, c.source, c.is_archived, c.updated_at "
            "FROM conversation_fts f JOIN conversations c ON c.fts_rowid = f.rowid "
            "WHERE conversation_fts MATCH ? ORDER BY c.updated_at DESC LIMIT ?"
        )
        rows = connection.execute(sql, (query, limit)).fetchall()
    except sqlite3.Error:
        return []
    finally:
        connection.close()
    return [
        {
            "id": row[0],
            "title": row[1],
            "source": row[2],
            "archived": bool(row[3]),
            "updated_ms": row[4],
        }
        for row in rows
    ]


def index_bodies(conversation_id: str) -> str:
    """The index's truncated body for one conversation, used only as a hint."""
    if not os.path.exists(INDEX_DB):
        return ""
    connection = sqlite3.connect(f"file:{INDEX_DB}?mode=ro", uri=True)
    try:
        row = connection.execute(
            "SELECT f.body FROM conversation_fts f JOIN conversations c "
            "ON c.fts_rowid = f.rowid WHERE c.id = ?",
            (conversation_id,),
        ).fetchone()
    except sqlite3.Error:
        return ""
    finally:
        connection.close()
    return row[0] if row else ""


def format_ms(value: int | None) -> str:
    if not value:
        return "-"
    moment = dt.datetime.fromtimestamp(value / 1000)
    return moment.strftime("%Y-%m-%d %H:%M")


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def render_markdown(
    records: list[dict[str, Any]],
    conversation_id: str,
    project_dir: str,
    include_tools: bool,
    include_events: bool,
) -> str:
    lines: list[str] = [
        f"# Cursor conversation {conversation_id}",
        "",
        f"- Workspace: `{project_dir}`",
        f"- Records: {len(records)}",
        "",
        "---",
        "",
    ]
    for role, record in iteration(records):
        if role == "event":
            if include_events:
                lines += [
                    f"> turn ended: {record.get('status', '?')} "
                    f"{record.get('error') or ''}".rstrip(),
                    "",
                ]
            continue
        for block in content_blocks(record):
            kind = block.get("type")
            if kind == "text":
                text = block_text(block)
                if not text.strip():
                    continue
                text = strip_envelope(text) if role == "user" else text
                prefix = "## 用户" if role == "user" else "## 助手"
                lines += [prefix, "", text.rstrip(), ""]
            elif kind == "tool_use" and include_tools:
                lines += [f"`{tool_summary(block)}`", ""]
    return "\n".join(lines)


def render_skeleton(records: list[dict[str, Any]]) -> str:
    """A cheap map of a long conversation: turn index, role, sizes, tool names."""
    lines: list[str] = []
    for position, (role, record) in enumerate(iteration(records)):
        texts = [
            block_text(block)
            for block in content_blocks(record)
            if block.get("type") == "text"
        ]
        tools = [
            str(block.get("name") or "tool")
            for block in content_blocks(record)
            if block.get("type") == "tool_use"
        ]
        if role == "event":
            lines.append(f"[{position}] event :: {record.get('error') or record.get('status')}")
            continue
        prose = " ".join(texts).strip().replace("\n", " ")
        head = prose[:120] if prose else ""
        tool_part = f" tools={','.join(tools)}" if tools else ""
        size_part = f" text={sum(len(t) for t in texts)}" if texts else ""
        lines.append(f"[{position}] {role}{size_part}{tool_part} :: {head}")
    return "\n".join(lines)


def render_stats(conversation_id: str, project_dir: str, path: str) -> str:
    records = load_records(path)
    counts: dict[str, int] = {}
    for role, _ in iteration(records):
        counts[role] = counts.get(role, 0) + 1
    events = [
        record
        for _, record in iteration(records)
        if record.get("type") == "turn_ended"
    ]
    first_user = ""
    for role, record in iteration(records):
        if role == "user":
            first_user = strip_envelope(
                " ".join(block_text(b) for b in content_blocks(record) if b.get("type") == "text")
            ).strip().replace("\n", " ")[:100]
            break
    lines = [
        f"id       {conversation_id}",
        f"path     {path}",
        f"workspace {project_dir}",
        f"size     {os.path.getsize(path)} bytes",
        f"records  {len(records)} ({counts.get('user', 0)} user, "
        f"{counts.get('assistant', 0)} assistant, {counts.get('event', 0)} events)",
        f"opened   {first_user or '-'}",
    ]
    for event in events:
        lines.append(f"ended    {event.get('status', '?')} — {event.get('error') or ''}")
    for extra in subagent_paths(path):
        lines.append(f"subagent {os.path.basename(extra)}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Subcommands
# --------------------------------------------------------------------------- #


def cmd_list(args: argparse.Namespace) -> int:
    rows: list[dict[str, Any]] = []
    for conversation_id, project_dir, path in transcript_paths(args.workspace):
        stat = os.stat(path)
        rows.append(
            {
                "id": conversation_id,
                "workspace": project_dir,
                "mtime": stat.st_mtime,
                "size": stat.st_size,
            }
        )
    rows.sort(key=lambda row: row["mtime"], reverse=True)
    if not rows:
        print("no transcripts found", file=sys.stderr)
        return 1
    for row in rows[: args.limit]:
        stamp = dt.datetime.fromtimestamp(row["mtime"]).strftime("%Y-%m-%d %H:%M")
        label = os.path.basename(row["workspace"].rstrip("/"))
        print(f"{stamp}  {row['size']:>8}  {row['id']}  {label}")
    print(f"\n{len(rows)} transcripts total", file=sys.stderr)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    hits = index_rows(args.query, args.limit)
    if not hits:
        print(
            "index returned nothing (query syntax, or the index is unavailable) — "
            "fall back to `find`",
            file=sys.stderr,
        )
        return 1
    for hit in hits:
        try:
            project_dir, path = find_transcript(hit["id"])
            where = project_dir
        except SystemExit:
            where = "(transcript not on disk)"
            path = ""
        print(f"{format_ms(hit['updated_ms'])}  {hit['id']}  {hit['title']}")
        print(f"    {where}")
        if path and args.preview:
            body = index_bodies(hit["id"])
            snippet = body[: args.preview].replace("\n", " ")
            if snippet:
                print(f"    {snippet}")
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    pattern = re.compile(args.pattern, re.IGNORECASE if args.ignore_case else 0)
    hits = 0
    for conversation_id, project_dir, path in transcript_paths(args.workspace):
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, 1):
                if not pattern.search(line):
                    continue
                hits += 1
                print(f"{conversation_id}  {os.path.basename(project_dir)}  line {number}")
                if args.show:
                    snippet = line.strip()[: args.show]
                    print(f"    {snippet}")
                if hits >= args.limit:
                    print(f"\nstopped at {args.limit} matches", file=sys.stderr)
                    return 0
    print(f"\n{hits} matching lines", file=sys.stderr)
    return 0 if hits else 1


def cmd_read(args: argparse.Namespace) -> int:
    project_dir, path = find_transcript(args.id)
    records = load_records(path)
    if args.skeleton:
        print(render_skeleton(records))
        return 0
    if args.tail:
        records = records[-args.tail :]
    print(
        render_markdown(
            records,
            os.path.basename(path)[: -len(".jsonl")],
            project_dir,
            include_tools=args.tools,
            include_events=True,
        )
    )
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    if args.id:
        project_dir, path = find_transcript(args.id)
        print(render_stats(os.path.basename(path)[: -len(".jsonl")], project_dir, path))
        return 0
    for conversation_id, project_dir, path in sorted(
        transcript_paths(args.workspace), key=lambda item: os.stat(item[2]).st_mtime
    ):
        print(render_stats(conversation_id, project_dir, path))
        print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    listing = sub.add_parser("list", help="list conversations, newest first")
    listing.add_argument("--workspace", help="filter by workspace slug substring")
    listing.add_argument("--limit", type=int, default=40)
    listing.set_defaults(func=cmd_list)

    search = sub.add_parser("search", help="search the Cursor FTS index")
    search.add_argument("query", help="FTS5 query, e.g. 'visual tension' or '\"exact phrase\"'")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--preview", type=int, default=200, help="body chars to show, 0 to hide")
    search.set_defaults(func=cmd_search)

    finder = sub.add_parser("find", help="regex-grep raw JSONL across transcripts")
    finder.add_argument("pattern")
    finder.add_argument("--workspace")
    finder.add_argument("--limit", type=int, default=40)
    finder.add_argument("--show", type=int, default=200, help="chars of the matching line, 0 to hide")
    finder.add_argument("-i", "--ignore-case", action="store_true")
    finder.set_defaults(func=cmd_find)

    reader = sub.add_parser("read", help="render one conversation as Markdown")
    reader.add_argument("id", help="conversation id or unambiguous prefix")
    reader.add_argument("--skeleton", action="store_true", help="one line per turn, no prose")
    reader.add_argument("--tail", type=int, help="only the last N records")
    reader.add_argument("--tools", action="store_true", help="include tool invocations")
    reader.set_defaults(func=cmd_read)

    stats = sub.add_parser("stats", help="size, turn count, and end status")
    stats.add_argument("id", nargs="?", help="conversation id or prefix; omit for all")
    stats.add_argument("--workspace")
    stats.set_defaults(func=cmd_stats)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
