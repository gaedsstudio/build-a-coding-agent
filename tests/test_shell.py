from pathlib import Path
import importlib.util


def load_tools():
    path = Path(__file__).parents[1] / "04-shell-execution" / "tools.py"
    spec = importlib.util.spec_from_file_location("chapter04_tools", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_shell_blocks_unlisted_executable(tmp_path):
    tools = load_tools()
    workspace = tools.Workspace(tmp_path / "workspace")
    result = tools.run_command(workspace, "curl https://example.com")
    assert "not allowed" in result


def test_python_command_runs_inside_workspace(tmp_path):
    tools = load_tools()
    workspace = tools.Workspace(tmp_path / "workspace")
    workspace.write_file("demo.py", "print('inside')\n")
    result = tools.run_command(workspace, "python demo.py")
    assert "exit_code=0" in result
    assert "inside" in result
