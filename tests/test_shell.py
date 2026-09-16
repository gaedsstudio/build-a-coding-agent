from pathlib import Path
import importlib.util

import pytest


CHAPTERS = [
    "04-shell-execution",
    "05-code-search",
    "06-context-management",
    "07-planning",
    "08-git-diff",
]


def load_tools(chapter: str):
    path = Path(__file__).parents[1] / chapter / "tools.py"
    spec = importlib.util.spec_from_file_location(f"{chapter.replace('-', '_')}_tools", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("chapter", CHAPTERS)
def test_shell_blocks_unlisted_executable(chapter, tmp_path):
    tools = load_tools(chapter)
    workspace = tools.Workspace(tmp_path / "workspace")
    result = tools.run_command(workspace, "curl https://example.com")
    assert "not allowed" in result


@pytest.mark.parametrize("chapter", CHAPTERS)
def test_shell_blocks_allowlist_path_aliases(chapter, tmp_path):
    tools = load_tools(chapter)
    workspace = tools.Workspace(tmp_path / "workspace")
    assert "paths are not allowed" in tools.run_command(workspace, "./python --version")
    assert "paths are not allowed" in tools.run_command(workspace, "/tmp/python --version")
    assert "paths are not allowed" in tools.run_command(workspace, "..\\python --version")


@pytest.mark.parametrize("chapter", CHAPTERS)
def test_agent_api_key_is_not_inherited_by_child_process(chapter, tmp_path, monkeypatch):
    tools = load_tools(chapter)
    workspace = tools.Workspace(tmp_path / "workspace")
    monkeypatch.setenv("AGENT_API_KEY", "secret-that-must-not-leak")

    result = tools.run_command(
        workspace,
        'python -c "import os; print(os.getenv(\'AGENT_API_KEY\'))"',
    )

    assert "exit_code=0" in result
    assert "secret-that-must-not-leak" not in result
    assert "None" in result


def test_python_command_runs_inside_workspace(tmp_path):
    tools = load_tools("04-shell-execution")
    workspace = tools.Workspace(tmp_path / "workspace")
    workspace.write_file("demo.py", "print('inside')\n")
    result = tools.run_command(workspace, "python demo.py")
    assert "exit_code=0" in result
    assert "inside" in result
