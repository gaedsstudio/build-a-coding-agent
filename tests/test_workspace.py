from pathlib import Path
import importlib.util


def load_tools():
    path = Path(__file__).parents[1] / "03-filesystem" / "tools.py"
    spec = importlib.util.spec_from_file_location("chapter03_tools", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_workspace_blocks_parent_escape(tmp_path):
    tools = load_tools()
    workspace = tools.Workspace(tmp_path / "workspace")

    try:
        workspace.resolve("../secret.txt")
    except PermissionError:
        pass
    else:
        raise AssertionError("parent traversal should be blocked")


def test_workspace_roundtrip(tmp_path):
    tools = load_tools()
    workspace = tools.Workspace(tmp_path / "workspace")

    workspace.write_file("src/demo.py", "print('ok')\n")
    assert workspace.read_file("src/demo.py") == "print('ok')\n"
    assert "src/demo.py" in workspace.list_files()
