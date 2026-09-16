from __future__ import annotations

import json
from pathlib import Path

from llm import chat
from tools import Workspace


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files inside the coding workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "default": "."}},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file inside the coding workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or replace a UTF-8 text file inside the coding workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
        },
    },
]


def execute(workspace: Workspace, name: str, args: dict) -> str:
    if name == "list_files":
        return workspace.list_files(str(args.get("path", ".")))
    if name == "read_file":
        return workspace.read_file(str(args["path"]))
    if name == "write_file":
        return workspace.write_file(str(args["path"]), str(args["content"]))
    raise ValueError(f"Unknown tool: {name}")


def run(task: str) -> str:
    workspace = Workspace(Path(__file__).parent / "workspace")
    messages = [
        {
            "role": "system",
            "content": (
                "You are a small coding agent. Inspect files before editing them. "
                "Work only through the provided tools. When the task is complete, summarize the change."
            ),
        },
        {"role": "user", "content": task},
    ]

    for _ in range(20):
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

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result,
                }
            )

    return "Agent stopped after reaching the tool-step limit."


def main() -> None:
    task = input("Task > ").strip()
    if task:
        print("\nAgent >", run(task))


if __name__ == "__main__":
    main()
