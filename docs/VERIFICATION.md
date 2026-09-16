# Verification

This repository treats verification as part of the agent design, not as a final cleanup step.

## What CI checks

Every push and pull request runs on Python **3.11, 3.12, and 3.13**.

For each version CI performs four layers:

1. **Compilation** — every implemented chapter, test, and verification script must compile.
2. **Repository verification** — chapter structure, tool schemas, subprocess safety invariants, obvious committed secrets, and forbidden `eval` / `exec` calls are checked.
3. **Regression tests** — workspace boundaries, shell restrictions, context budgeting, planning, code search, Git diff behavior, and calculator validation are exercised.
4. **Cross-version compatibility** — the same checks must pass on every supported Python version.

Run the same verification locally:

```bash
python -m compileall -q \
  00-hello-agent 01-agent-loop 02-tool-calling 03-filesystem \
  04-shell-execution 05-code-search 06-context-management \
  07-planning 08-git-diff tests scripts

python scripts/verify_repository.py
pytest -q
```

## Security regressions that are explicitly tested

### Executable allowlist bypass

An allowlist must validate the command token itself, not only its basename.

These are rejected even though they end in an allowlisted name:

```text
./python
/tmp/python
..\python
```

Otherwise a model could execute a different file that merely happens to be named `python`.

### Secret inheritance

Development commands do not inherit common agent/provider secret variables such as `AGENT_API_KEY`.

This is a narrow teaching boundary. It is **not** a substitute for the isolation introduced later in the sandbox chapter.

### Context overflow

Pinned context (system rules, original task, and later the active plan) is mandatory. If mandatory context alone exceeds the configured budget, the agent now fails with a clear error instead of silently violating its own budget.

### Calculator execution

The chapter 02 calculator uses a bounded AST evaluator rather than Python `eval()`.

Only basic arithmetic is accepted. Calls, exponentiation, floor division, modulo, oversized values, and excessively complex expressions are rejected.

## What these checks do not prove

Passing CI does **not** make the tutorial agent a production sandbox.

In particular:

- `python` can still execute arbitrary Python code inside the host process boundary.
- an executable allowlist is not OS isolation.
- filesystem tools are scoped, but shell commands need the later sandbox chapter for strong host isolation.
- token counts are deliberately approximate until provider-specific counting is introduced.
- model behavior itself is nondeterministic and is not covered by these unit tests.

Those limitations are intentional. Each later chapter exists because an earlier boundary is not enough.

## Rule for future chapters

A roadmap box should not be marked complete until:

- the example runs,
- its main failure mode has a regression test,
- CI verifies the new boundary,
- the README explains what is still not guaranteed.
