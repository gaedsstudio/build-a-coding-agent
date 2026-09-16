from __future__ import annotations

import os
from pathlib import Path
import shlex
import subprocess


class Workspace:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative: str) -> Path:
        candidate = (self.root / relative).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise PermissionError(f"Path escapes workspace: {relative}") from exc
        return candidate

    def list_files(self, path: str = ".") -> str:
        target = self.resolve(path)
        if not target.exists():
            return f"ERROR: path does not exist: {path}"
        if target.is_file():
            return str(target.relative_to(self.root))

        entries = []
        for item in sorted(target.rglob("*")):
            if item.is_file():
                entries.append(str(item.relative_to(self.root)))
            if len(entries) >= 200:
                entries.append("... truncated ...")
                break
        return "\n".join(entries) or "(empty)"

    def read_file(self, path: str) -> str:
        target = self.resolve(path)
        if not target.is_file():
            return f"ERROR: not a file: {path}"
        data = target.read_text(encoding="utf-8")
        if len(data) > 40_000:
            return data[:40_000] + "\n... truncated ..."
        return data

    def write_file(self, path: str, content: str) -> str:
        target = self.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} characters to {path}"


ALLOWED_EXECUTABLES = {"python", "python3", "pytest", "git", "rg"}
SENSITIVE_ENV_KEYS = {
    "AGENT_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
}


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in SENSITIVE_ENV_KEYS:
        env.pop(key, None)
    return env


def run_command(workspace: Workspace, command: str, timeout_seconds: int = 20) -> str:
    args = shlex.split(command)
    if not args:
        return "ERROR: empty command"

    requested = args[0]
    if requested != Path(requested).name or "/" in requested or "\\" in requested:
        return "ERROR: executable paths are not allowed; use a bare allowlisted command name"

    executable = requested.lower()
    if executable not in ALLOWED_EXECUTABLES:
        return f"ERROR: executable is not allowed in this chapter: {executable}"

    timeout_seconds = max(1, min(int(timeout_seconds), 60))

    try:
        completed = subprocess.run(
            args,
            cwd=workspace.root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
            env=_subprocess_env(),
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: command timed out after {timeout_seconds}s"
    except FileNotFoundError:
        return f"ERROR: executable not found: {executable}"

    output = (
        f"exit_code={completed.returncode}\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
    if len(output) > 30_000:
        output = output[:30_000] + "\n... truncated ..."
    return output
