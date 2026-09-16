from __future__ import annotations

import ast
import math
import operator
from typing import Callable


MAX_EXPRESSION_CHARS = 200
MAX_AST_NODES = 64
MAX_ABS_VALUE = 1_000_000_000_000

BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _bounded(value: int | float) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Only numeric values are supported.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Result must be finite.")
    if abs(value) > MAX_ABS_VALUE:
        raise ValueError(f"Absolute value may not exceed {MAX_ABS_VALUE}.")
    return value


def _evaluate(node: ast.AST) -> int | float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)

    if isinstance(node, ast.Constant):
        return _bounded(node.value)

    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
        operand = _evaluate(node.operand)
        return _bounded(UNARY_OPERATORS[type(node.op)](operand))

    if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        return _bounded(BINARY_OPERATORS[type(node.op)](left, right))

    raise ValueError("Only +, -, *, /, unary +/- and parentheses are supported.")


def calculate(expression: str) -> str:
    expression = expression.strip()
    if not expression:
        raise ValueError("Expression must not be empty.")
    if len(expression) > MAX_EXPRESSION_CHARS:
        raise ValueError(f"Expression is too long (max {MAX_EXPRESSION_CHARS} characters).")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("Expression is not valid arithmetic.") from exc

    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise ValueError("Expression is too complex.")

    return str(_evaluate(tree))
