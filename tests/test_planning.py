from pathlib import Path
import importlib.util
import sys
import pytest


def load_plan():
    path = Path(__file__).parents[1] / "07-planning" / "plan.py"
    spec = importlib.util.spec_from_file_location("chapter07_plan", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_plan_requires_small_nontrivial_plan():
    plan = load_plan().Plan()
    with pytest.raises(ValueError):
        plan.set_steps(["only one"])
    plan.set_steps(["find code", "edit code"])
    assert len(plan.steps) == 2


def test_done_step_requires_evidence():
    plan = load_plan().Plan()
    plan.set_steps(["find code", "verify"])
    with pytest.raises(ValueError):
        plan.update_step(0, "done")
    rendered = plan.update_step(0, "done", "search found services/users.py")
    assert "services/users.py" in rendered


def test_plan_can_be_revised():
    plan = load_plan().Plan()
    plan.set_steps(["read app.py", "edit app.py"])
    plan.set_steps(["search formatter", "edit formatter", "verify"], reason="app.py delegates formatting")
    assert plan.revision == 1
    assert plan.last_revision_reason == "app.py delegates formatting"
    assert plan.steps[0].text == "search formatter"


def test_plan_rejects_invalid_status_and_index():
    plan = load_plan().Plan()
    plan.set_steps(["a", "b"])
    with pytest.raises(ValueError):
        plan.update_step(0, "finished", "x")
    with pytest.raises(IndexError):
        plan.update_step(9, "done", "x")
