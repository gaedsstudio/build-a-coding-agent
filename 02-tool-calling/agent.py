from __future__ import annotations

import json
from llm import chat


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate basic arithmetic with +, -, *, / and parentheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    }
]


def calculate(expression: str) -> str:
    allowed = set("0123456789+-*/(). %")
    if not expression or any(ch not in allowed for ch in expression):
        raise ValueError("Expression contains unsupported characters.")
    # No builtins are exposed. This chapter keeps the tool intentionally tiny.
    return str(eval(expression, {"__builtins__": {}}, {}))


def execute(name: str, arguments: dict) -> str:
    if name == "calculate":
        return calculate(str(arguments["expression"]))
    raise ValueError(f"Unknown tool: {name}")


def run(task: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a coding agent tutorial. Use tools when they make the answer more reliable.",
        },
        {"role": "user", "content": task},
    ]

    for _ in range(8):
        reply = chat(messages, tools=TOOLS)
        messages.append(reply)

        calls = reply.get("tool_calls") or []
        if not calls:
            return reply.get("content") or ""

        for call in calls:
            function = call["function"]
            args = json.loads(function.get("arguments") or "{}")
            try:
                result = execute(function["name"], args)
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
    task = input("You > ").strip()
    if task:
        print("\nAgent >", run(task))


if __name__ == "__main__":
    main()
