from __future__ import annotations

from pathlib import Path
import re
import shlex
import subprocess


SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rs",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".rb", ".php", ".swift", ".md",
    ".txt", ".toml", ".yaml", ".yml", ".json", ".html", ".css", ".sql",
}


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

    def _iter_files(self, path: str = "."):
        target = self.resolve(path)
        if target.is_file():
            yield target
            return
        for item in sorted(target.rglob("*")):
            if not item.is_file():
                continue
            rel_parts = item.relative_to(self.root).parts
            if any(part in SKIP_DIRS for part in rel_parts):
                continue
            yield item

    def list_files(self, path: str = ".") -> str:
        target = self.resolve(path)
        if not target.exists():
            return f"ERROR: path does not exist: {path}"
        entries = []
        for item in self._iter_files(path):
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

    def search_code(self, query: str, path: str = ".", max_results: int = 40) -> str:
        """Search filenames and text without dumping the whole repository into context."""
        query = query.strip()
        if not query:
            return "ERROR: query must not be empty"
        max_results = max(1, min(int(max_results), 100))
        needle = query.casefold()
        matches: list[tuple[int, str]] = []

        for file in self._iter_files(path):
            rel = str(file.relative_to(self.root))
            if needle in rel.casefold():
                matches.append((3, f"{rel}  [path match]"))

            if file.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            for line_no, line in enumerate(text.splitlines(), start=1):
                if needle not in line.casefold():
                    continue
                snippet = re.sub(r"\s+", " ", line.strip())
                if len(snippet) > 180:
                    snippet = snippet[:177] + "..."
                score = 2 if re.search(rf"\b{re.escape(query)}\b", line, re.IGNORECASE) else 1
                matches.append((score, f"{rel}:{line_no}: {snippet}"))
                if len(matches) >= max_results * 4:
                    break

        if not matches:
            return f"No matches for {query!r} under {path!r}."

        matches.sort(key=lambda item: (-item[0], item[1]))
        seen = set()
        output = []
        for _, item in matches:
            if item in seen:
                continue
            seen.add(item)
            output.append(item)
            if len(output) >= max_results:
                break
        return "\n".join(output)


ALLOWED_EXECUTABLES = {"python", "python3", "pytest", "git", "rg"}


def run_command(workspace: Workspace, command: str, timeout_seconds: int = 20) -> str:
    args = shlex.split(command)
    if not args:
        return "ERROR: empty command"
    executable = Path(args[0]).name.lower()
    if executable not in ALLOWED_EXECUTABLES:
        return f"ERROR: executable is not allowed in this chapter: {executable}"
    timeout_seconds = max(1, min(int(timeout_seconds), 60))
    try:
        completed = subprocess.run(
            args, cwd=workspace.root, capture_output=True, text=True,
            timeout=timeout_seconds, shell=False,
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: command timed out after {timeout_seconds}s"
    except FileNotFoundError:
        return f"ERROR: executable not found: {executable}"
    output = f"exit_code={completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    return output[:30_000] + ("\n... truncated ..." if len(output) > 30_000 else "")
