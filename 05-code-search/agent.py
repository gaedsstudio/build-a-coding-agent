from __future__ import annotations

import json
from pathlib import Path

from llm import chat
from tools import Workspace, run_command


TOOLS = [
    {"type": "function", "function": {"name": "list_files", "description": "List files inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "default": "."}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "search_code", "description": "Search filenames and source text. Use this before reading files when you do not know where relevant code lives.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "path": {"type": "string", "default": "."}, "max_results": {"type": "integer", "minimum": 1, "maximum": 100}}, "required": ["query"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read a UTF-8 file inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "write_file", "description": "Create or replace a UTF-8 file inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "run_command", "description": "Run an allowlisted development command in the workspace.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60}}, "required": ["command"], "additionalProperties": False}}},
]


def execute(workspace: Workspace, name: str, args: dict) -> str:
    if name == "list_files": return workspace.list_files(str(args.get("path", ".")))
    if name == "search_code": return workspace.search_code(str(args["query"]), str(args.get("path", ".")), int(args.get("max_results", 40)))
    if name == "read_file": return workspace.read_file(str(args["path"]))
    if name == "write_file": return workspace.write_file(str(args["path"]), str(args["content"]))
    if name == "run_command": return run_command(workspace, str(args["command"]), int(args.get("timeout_seconds", 20)))
    raise ValueError(f"Unknown tool: {name}")


def run(task: str) -> str:
    workspace = Workspace(Path(__file__).parent / "workspace")
    messages = [
        {"role": "system", "content": (
            "You are a coding agent. Do not read the entire repository by default. "
            "When you do not know where relevant code lives, search first, then read only likely files. "
            "Make the smallest change that solves the task and verify it when possible. "
            "Do not claim verification unless a tool result confirms it."
        )},
        {"role": "user", "content": task},
    ]
    for _ in range(30):
        reply = chat(messages, tools=TOOLS)
        messages.append(reply)
        calls = reply.get("tool_calls") or []
        if not calls:
            return reply.get("content") or ""
        for call in calls:
            fn = call["function"]
            try:
                args = json.loads(fn.get("arguments") or "{}")
                result = execute(workspace, fn["name"], args)
            except Exception as exc:
                result = f"ERROR: {type(exc).__name__}: {exc}"
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return "Agent stopped after reaching the tool-step limit."


def main() -> None:
    task = input("Task > ").strip()
    if task:
        print("\nAgent >", run(task))


if __name__ == "__main__":
    main()
