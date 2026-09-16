from pathlib import Path
import importlib.util

import pytest


def load_calculator():
    path = Path(__file__).parents[1] / "02-tool-calling" / "calculator.py"
    spec = importlib.util.spec_from_file_location("chapter02_calculator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_calculator_handles_basic_arithmetic():
    calculate = load_calculator().calculate
    assert calculate("(12 + 3) * 4") == "60"
    assert calculate("7 / 2") == "3.5"
    assert calculate("-5 + 2") == "-3"


@pytest.mark.parametrize("expression", ["2 ** 10", "7 // 2", "5 % 2", "abs(1)", "True + 1"])
def test_calculator_rejects_unsupported_syntax(expression):
    with pytest.raises(ValueError):
        load_calculator().calculate(expression)


def test_calculator_rejects_oversized_values():
    with pytest.raises(ValueError, match="Absolute value"):
        load_calculator().calculate("1000000000000 * 2")


def test_calculator_rejects_overlong_expression():
    with pytest.raises(ValueError, match="too long"):
        load_calculator().calculate("1+" * 101 + "1")
