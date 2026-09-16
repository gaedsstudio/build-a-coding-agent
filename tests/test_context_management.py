from pathlib import Path
import importlib.util
import sys


def load_context():
    path = Path(__file__).parents[1] / "06-context-management" / "context.py"
    spec = importlib.util.spec_from_file_location("chapter06_context", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assistant_turn(call_id: str, content: str = "x"):
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": call_id,
            "type": "function",
            "function": {"name": "read_file", "arguments": '{"path":"demo.py"}'},
        }],
    }, [{"role": "tool", "tool_call_id": call_id, "content": content}]


def test_context_keeps_pinned_messages():
    ctx = load_context().ContextWindow("system rule", "fix the bug", max_tokens=256)
    messages = ctx.messages()
    assert messages[0] == {"role": "system", "content": "system rule"}
    assert messages[1] == {"role": "user", "content": "fix the bug"}


def test_context_drops_oldest_turns_first():
    module = load_context()
    ctx = module.ContextWindow("s", "u", max_tokens=180)

    first, first_tools = assistant_turn("call-old", "old " * 80)
    second, second_tools = assistant_turn("call-new", "new " * 20)
    ctx.add_turn(first, first_tools)
    ctx.add_turn(second, second_tools)

    messages = ctx.messages()
    ids = [m.get("tool_call_id") for m in messages if m.get("role") == "tool"]
    assert "call-new" in ids
    assert "call-old" not in ids
    report = ctx.report()
    assert report.kept_turns == 1
    assert report.dropped_turns == 1


def test_context_keeps_tool_exchange_atomic():
    module = load_context()
    ctx = module.ContextWindow("s", "u", max_tokens=512)
    assistant, tools = assistant_turn("call-1", "result")
    ctx.add_turn(assistant, tools)

    messages = ctx.messages()
    assistant_ids = {
        call["id"]
        for m in messages
        if m.get("role") == "assistant"
        for call in m.get("tool_calls", [])
    }
    tool_ids = {m["tool_call_id"] for m in messages if m.get("role") == "tool"}
    assert assistant_ids == tool_ids == {"call-1"}


def test_estimator_is_deterministic_and_nonzero():
    module = load_context()
    assert module.estimate_tokens("") == 1
    assert module.estimate_tokens("abcdefgh") == 2
    assert module.estimate_tokens({"role": "user", "content": "hello"}) > 1
