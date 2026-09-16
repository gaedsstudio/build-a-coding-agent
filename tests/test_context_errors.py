from pathlib import Path
import importlib.util
import sys

import pytest


ROOT = Path(__file__).parents[1]


def load_context(chapter: str):
    path = ROOT / chapter / "context.py"
    name = f"{chapter.replace('-', '_')}_context_errors"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("chapter", ["06-context-management", "07-planning", "08-git-diff"])
def test_pinned_context_overflow_is_rejected(chapter):
    module = load_context(chapter)
    ctx = module.ContextWindow("system " * 200, "task " * 200, max_tokens=128)

    with pytest.raises(module.ContextBudgetError, match="pinned context"):
        ctx.messages()


@pytest.mark.parametrize("chapter", ["07-planning", "08-git-diff"])
def test_extra_pinned_plan_can_trigger_clear_overflow(chapter):
    module = load_context(chapter)
    ctx = module.ContextWindow("system", "task", max_tokens=128)
    huge_plan = [{"role": "system", "content": "plan " * 300}]

    with pytest.raises(module.ContextBudgetError, match="task/plan"):
        ctx.messages(extra_pinned=huge_plan)
