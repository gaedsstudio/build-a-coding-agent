from pathlib import Path
import importlib.util


def load_tools():
    path = Path(__file__).parents[1] / "05-code-search" / "tools.py"
    spec = importlib.util.spec_from_file_location("chapter05_tools", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_search_finds_text_and_line_number(tmp_path):
    tools = load_tools()
    workspace = tools.Workspace(tmp_path / "workspace")
    workspace.write_file("src/users.py", "def format_user(user):\n    return user['name']\n")
    result = workspace.search_code("format_user")
    assert "src/users.py:1:" in result
    assert "def format_user" in result


def test_search_skips_cache_directories(tmp_path):
    tools = load_tools()
    workspace = tools.Workspace(tmp_path / "workspace")
    workspace.write_file("src/app.py", "needle = 1\n")
    workspace.write_file("__pycache__/generated.py", "needle = 2\n")
    result = workspace.search_code("needle")
    assert "src/app.py" in result
    assert "__pycache__" not in result


def test_search_stays_inside_workspace(tmp_path):
    tools = load_tools()
    workspace = tools.Workspace(tmp_path / "workspace")
    try:
        workspace.search_code("anything", "../")
    except PermissionError:
        pass
    else:
        raise AssertionError("search path traversal should be blocked")
