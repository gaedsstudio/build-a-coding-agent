from pathlib import Path
import importlib.util
import subprocess
import sys

import pytest


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_chapter():
    root = Path(__file__).parents[1] / "08-git-diff"
    tools = load_module("chapter08_tools", root / "tools.py")
    diff_tool = load_module("chapter08_diff", root / "diff_tool.py")
    return tools, diff_tool


def run_git(path: Path, *args: str, capture_output: bool = False):
    return subprocess.run(
        ["git", *args],
        cwd=path,
        check=True,
        capture_output=capture_output,
        timeout=10,
        shell=False,
    )


def init_repo(path: Path):
    run_git(path, "init", capture_output=True)
    run_git(path, "config", "user.email", "test@example.com")
    run_git(path, "config", "user.name", "Test")


def commit_all(path: Path):
    run_git(path, "add", ".")
    run_git(path, "commit", "-m", "baseline", capture_output=True)


def test_git_diff_shows_tracked_edit(tmp_path):
    tools, diff_tool = load_chapter()
    workspace = tools.Workspace(tmp_path / "repo")
    init_repo(workspace.root)
    workspace.write_file("demo.py", 'label = "User:"\n')
    commit_all(workspace.root)
    workspace.write_file("demo.py", 'label = "Member:"\n')

    diff = diff_tool.git_diff(workspace)
    assert "diff --git a/demo.py b/demo.py" in diff
    assert '-label = "User:"' in diff
    assert '+label = "Member:"' in diff


def test_git_diff_can_scope_to_path(tmp_path):
    tools, diff_tool = load_chapter()
    workspace = tools.Workspace(tmp_path / "repo")
    init_repo(workspace.root)
    workspace.write_file("a.py", "x = 1\n")
    workspace.write_file("b.py", "y = 1\n")
    commit_all(workspace.root)
    workspace.write_file("a.py", "x = 2\n")
    workspace.write_file("b.py", "y = 2\n")

    diff = diff_tool.git_diff(workspace, "a.py")
    assert "a.py" in diff
    assert "b.py" not in diff


def test_git_diff_reports_no_change(tmp_path):
    tools, diff_tool = load_chapter()
    workspace = tools.Workspace(tmp_path / "repo")
    init_repo(workspace.root)
    workspace.write_file("demo.py", "x = 1\n")
    commit_all(workspace.root)
    assert diff_tool.git_diff(workspace) == "(no diff)"


def test_git_diff_blocks_workspace_escape(tmp_path):
    tools, diff_tool = load_chapter()
    workspace = tools.Workspace(tmp_path / "repo")
    with pytest.raises(PermissionError):
        diff_tool.git_diff(workspace, "../outside")
