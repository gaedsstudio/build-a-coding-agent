from __future__ import annotations

import subprocess


def git_diff(workspace, path: str = ".", max_chars: int = 30_000) -> str:
    """Return a scoped unified diff for tracked changes inside the workspace."""
    target = workspace.resolve(path)
    if not target.exists():
        return f"ERROR: path does not exist: {path}"

    relative = "." if target == workspace.root else str(target.relative_to(workspace.root))
    max_chars = max(1_000, min(int(max_chars), 100_000))

    try:
        completed = subprocess.run(
            ["git", "diff", "--no-ext-diff", "--unified=3", "--", relative],
            cwd=workspace.root,
            capture_output=True,
            text=True,
            timeout=20,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return "ERROR: git diff timed out"
    except FileNotFoundError:
        return "ERROR: git executable not found"

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        return f"ERROR: git diff failed ({completed.returncode}): {detail}"

    output = completed.stdout
    if not output:
        return "(no diff)"
    if len(output) > max_chars:
        return output[:max_chars] + "\n... diff truncated ..."
    return output
