from __future__ import annotations

import ast
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).parents[1]

CHAPTER_FILES = {
    "00-hello-agent": {"README.md", "agent.py", "llm.py"},
    "01-agent-loop": {"README.md", "agent.py", "llm.py"},
    "02-tool-calling": {"README.md", "agent.py", "calculator.py", "llm.py"},
    "03-filesystem": {"README.md", "agent.py", "llm.py", "tools.py"},
    "04-shell-execution": {"README.md", "agent.py", "llm.py", "tools.py"},
    "05-code-search": {"README.md", "agent.py", "llm.py", "tools.py"},
    "06-context-management": {"README.md", "agent.py", "context.py", "llm.py", "tools.py"},
    "07-planning": {"README.md", "agent.py", "context.py", "llm.py", "plan.py", "tools.py"},
    "08-git-diff": {"README.md", "agent.py", "context.py", "diff_tool.py", "llm.py", "plan.py", "tools.py"},
}

TEXT_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".json"}
SECRET_PATTERNS = {
    "OpenAI-style API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub personal token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


class VerificationError(Exception):
    pass


def add_error(errors: list[str], path: Path | str, message: str) -> None:
    try:
        display = Path(path).relative_to(ROOT)
    except (TypeError, ValueError):
        display = path
    errors.append(f"{display}: {message}")


def check_structure(errors: list[str]) -> None:
    for chapter, required in CHAPTER_FILES.items():
        chapter_dir = ROOT / chapter
        if not chapter_dir.is_dir():
            add_error(errors, chapter_dir, "implemented chapter directory is missing")
            continue
        for filename in sorted(required):
            if not (chapter_dir / filename).is_file():
                add_error(errors, chapter_dir / filename, "required checkpoint file is missing")


def parse_python(path: Path, errors: list[str]) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as exc:
        add_error(errors, path, f"cannot parse Python: {exc}")
        return None


def keyword_map(call: ast.Call) -> dict[str, ast.AST]:
    return {kw.arg: kw.value for kw in call.keywords if kw.arg is not None}


def is_subprocess_run(call: ast.Call) -> bool:
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "run"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "subprocess"
    )


def check_python_safety(path: Path, tree: ast.Module, errors: list[str]) -> None:
    function_stack: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
            function_stack.append(node.name)
            self.generic_visit(node)
            function_stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call) -> Any:
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                add_error(errors, path, f"line {node.lineno}: built-in {node.func.id}() is forbidden in tutorial code")

            if is_subprocess_run(node):
                keywords = keyword_map(node)
                if "timeout" not in keywords:
                    add_error(errors, path, f"line {node.lineno}: subprocess.run must set a timeout")

                shell = keywords.get("shell")
                if not isinstance(shell, ast.Constant) or shell.value is not False:
                    add_error(errors, path, f"line {node.lineno}: subprocess.run must set shell=False explicitly")

                if function_stack and function_stack[-1] == "run_command" and "env" not in keywords:
                    add_error(errors, path, f"line {node.lineno}: run_command must pass a scrubbed child environment")

            self.generic_visit(node)

    Visitor().visit(tree)


def literal_assignment(tree: ast.Module, name: str) -> Any | None:
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue

        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        else:
            targets = [node.target]
            value = node.value

        if value is None:
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            try:
                return ast.literal_eval(value)
            except (ValueError, TypeError, SyntaxError):
                return None
    return None


def check_tool_schemas(path: Path, tree: ast.Module, errors: list[str]) -> None:
    tools = literal_assignment(tree, "TOOLS")
    if tools is None:
        return
    if not isinstance(tools, list):
        add_error(errors, path, "TOOLS must be a literal list so the tutorial surface stays inspectable")
        return

    names: list[str] = []
    for index, tool in enumerate(tools):
        try:
            function = tool["function"]
            name = function["name"]
            parameters = function["parameters"]
        except (KeyError, TypeError):
            add_error(errors, path, f"TOOLS[{index}] is missing function/name/parameters")
            continue

        names.append(name)
        if parameters.get("type") != "object":
            add_error(errors, path, f"tool {name!r}: parameters.type must be 'object'")
        if parameters.get("additionalProperties") is not False:
            add_error(errors, path, f"tool {name!r}: additionalProperties must be false")

        properties = parameters.get("properties", {})
        required = parameters.get("required", [])
        unknown_required = [key for key in required if key not in properties]
        if unknown_required:
            add_error(errors, path, f"tool {name!r}: required keys missing from properties: {unknown_required}")

    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        add_error(errors, path, f"duplicate tool names: {duplicates}")


def check_python(errors: list[str]) -> None:
    paths = []
    for chapter in CHAPTER_FILES:
        paths.extend((ROOT / chapter).rglob("*.py"))
    paths.extend((ROOT / "tests").rglob("*.py"))
    paths.extend((ROOT / "scripts").rglob("*.py"))

    for path in sorted(set(paths)):
        tree = parse_python(path, errors)
        if tree is None:
            continue
        check_python_safety(path, tree, errors)
        if path.name == "agent.py":
            check_tool_schemas(path, tree, errors)


def check_obvious_secrets(errors: list[str]) -> None:
    roots = [ROOT / name for name in CHAPTER_FILES]
    roots += [ROOT / "tests", ROOT / "scripts", ROOT / "docs"]
    roots += [ROOT / "README.md", ROOT / "ROADMAP.md", ROOT / "CONTRIBUTING.md"]

    for root in roots:
        candidates = [root] if root.is_file() else root.rglob("*")
        for path in candidates:
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    add_error(errors, path, f"looks like a committed {label}")


def main() -> int:
    errors: list[str] = []
    check_structure(errors)
    check_python(errors)
    check_obvious_secrets(errors)

    if errors:
        print("repository verification FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print(f"repository verification passed ({len(CHAPTER_FILES)} implemented chapters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
