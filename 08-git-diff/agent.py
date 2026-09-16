from __future__ import annotations

import json
import os
from pathlib import Path

from context import ContextWindow
from diff_tool import git_diff
from llm import chat
from plan import Plan
from tools import Workspace, run_command


TOOLS = [
    {"type": "function", "function": {"name": "set_plan", "description": "Create or revise a short execution plan before multi-step work.", "parameters": {"type": "object", "properties": {"steps": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 6}, "reason": {"type": "string"}}, "required": ["steps"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "update_plan_step", "description": "Update one plan step. Mark done only with concrete evidence.", "parameters": {"type": "object", "properties": {"index": {"type": "integer", "minimum": 0}, "status": {"type": "string", "enum": ["pending", "in_progress", "done", "blocked"]}, "evidence": {"type": "string"}}, "required": ["index", "status"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "list_files", "description": "List files inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "default": "."}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "search_code", "description": "Search filenames and source text.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "path": {"type": "string", "default": "."}, "max_results": {"type": "integer", "minimum": 1, "maximum": 100}}, "required": ["query"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read a UTF-8 file inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "write_file", "description": "Create or replace a UTF-8 file inside the coding workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "git_diff", "description": "Inspect the unified Git diff for tracked workspace changes. Use after editing and before claiming the change is correct.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "default": "."}, "max_chars": {"type": "integer", "minimum": 1000, "maximum": 100000}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "run_command", "description": "Run an allowlisted development command in the workspace.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60}}, "required": ["command"], "additionalProperties": False}}},
]


SYSTEM = """You are a coding agent with bounded context, a mutable plan, and Git diff inspection.
For multi-step work, create a short plan before editing and revise it when evidence changes the approach.
Search before reading when code location is unknown. After editing tracked files, inspect git_diff before verification or claiming success.
Use the diff to catch accidental or unrelated edits. Mark plan steps done only with concrete tool evidence."""


def execute(workspace: Workspace, plan: Plan, name: str, args: dict) -> str:
    if name == "set_plan":
        return plan.set_steps(list(args["steps"]), str(args.get("reason", "")))
    if name == "update_plan_step":
        return plan.update_step(int(args["index"]), str(args["status"]), str(args.get("evidence", "")))
    if name == "list_files":
        return workspace.list_files(str(args.get("path", ".")))
    if name == "search_code":
        return workspace.search_code(str(args["query"]), str(args.get("path", ".")), int(args.get("max_results", 40)))
    if name == "read_file":
        return workspace.read_file(str(args["path"]))
    if name == "write_file":
        return workspace.write_file(str(args["path"]), str(args["content"]))
    if name == "git_diff":
        return git_diff(workspace, str(args.get("path", ".")), int(args.get("max_chars", 30_000)))
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
    plan = Plan()
    debug = os.environ.get("AGENT_CONTEXT_DEBUG") == "1"

    try:
        context = ContextWindow(SYSTEM, task, max_tokens=_context_budget())
    except ValueError as exc:
        return f"ERROR: invalid context configuration: {exc}"

    for _ in range(40):
        plan_snapshot = [{"role": "system", "content": "Current plan state:\n" + plan.render()}]
        try:
            messages = context.messages(extra_pinned=plan_snapshot)
        except ValueError as exc:
            return f"ERROR: context budget exceeded: {exc}"

        if debug:
            print(f"[context] {context.report().line()}")
            print("[plan]\n" + plan.render())

        reply = chat(messages, tools=TOOLS)
        calls = reply.get("tool_calls") or []
        if not calls:
            return reply.get("content") or ""

        tool_messages = []
        for call in calls:
            fn = call["function"]
            try:
                args = json.loads(fn.get("arguments") or "{}")
                result = execute(workspace, plan, fn["name"], args)
            except Exception as exc:
                result = f"ERROR: {type(exc).__name__}: {exc}"
            tool_messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
        context.add_turn(reply, tool_messages)

    return "Agent stopped after reaching the tool-step limit."


def main() -> None:
    task = input("Task > ").strip()
    if task:
        print("\nAgent >", run(task))


if __name__ == "__main__":
    main()
