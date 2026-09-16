from __future__ import annotations

import json
import os
from pathlib import Path

from context import ContextWindow
from llm import chat
from tools import Workspace, run_command


TOOLS = [
    {"type": "function", "function": {"name": "list_files", "description": "List files inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "default": "."}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "search_code", "description": "Search filenames and source text. Use this before reading files when you do not know where relevant code lives.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "path": {"type": "string", "default": "."}, "max_results": {"type": "integer", "minimum": 1, "maximum": 100}}, "required": ["query"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read a UTF-8 file inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "write_file", "description": "Create or replace a UTF-8 file inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "run_command", "description": "Run an allowlisted development command in the workspace.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60}}, "required": ["command"], "additionalProperties": False}}},
]


SYSTEM = """You are a coding agent with a bounded context window.
Search before reading when code location is unknown. Read only likely files.
Old tool exchanges may fall out of context, so keep decisions grounded in recent evidence.
Make the smallest useful edit and verify it when possible.
Do not claim verification unless a tool result confirms it."""


def execute(workspace: Workspace, name: str, args: dict) -> str:
    if name == "list_files":
        return workspace.list_files(str(args.get("path", ".")))
    if name == "search_code":
        return workspace.search_code(
            str(args["query"]),
            str(args.get("path", ".")),
            int(args.get("max_results", 40)),
        )
    if name == "read_file":
        return workspace.read_file(str(args["path"]))
    if name == "write_file":
        return workspace.write_file(str(args["path"]), str(args["content"]))
    if name == "run_command":
        return run_command(workspace, str(args["command"]), int(args.get("timeout_seconds", 20)))
    raise ValueError(f"Unknown tool: {name}")


def _context_budget() -> int:
    raw = os.environ.get("AGENT_CONTEXT_TOKENS", "12000")
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError("AGENT_CONTEXT_TOKENS must be an integer") from exc


def run(task: str) -> str:
    workspace = Workspace(Path(__file__).parent / "workspace")
    debug_context = os.environ.get("AGENT_CONTEXT_DEBUG") == "1"

    try:
        context = ContextWindow(SYSTEM, task, max_tokens=_context_budget())
    except ValueError as exc:
        return f"ERROR: invalid context configuration: {exc}"

    for _ in range(30):
        try:
            messages = context.messages()
        except ValueError as exc:
            return f"ERROR: context budget exceeded: {exc}"

        if debug_context:
            print(f"[context] {context.report().line()}")

        reply = chat(messages, tools=TOOLS)
        calls = reply.get("tool_calls") or []
        if not calls:
            return reply.get("content") or ""

        tool_messages = []
        for call in calls:
            fn = call["function"]
            try:
                args = json.loads(fn.get("arguments") or "{}")
                result = execute(workspace, fn["name"], args)
            except Exception as exc:
                result = f"ERROR: {type(exc).__name__}: {exc}"

            tool_messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result,
            })

        context.add_turn(reply, tool_messages)

    return "Agent stopped after reaching the tool-step limit."


def main() -> None:
    task = input("Task > ").strip()
    if task:
        print("\nAgent >", run(task))


if __name__ == "__main__":
    main()
