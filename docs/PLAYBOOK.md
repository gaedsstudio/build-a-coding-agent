# Coding Agent Playbook

The chapter READMEs teach the implementation. This file is the practical playbook for getting unstuck while building or extending the agent.

## The default investigation loop

When the agent does not know a codebase yet, prefer this order:

```text
1. list the project shape
2. search for a symbol / route / error string
3. read the smallest relevant files
4. form a concrete hypothesis
5. make the smallest edit
6. run the narrowest useful check
7. inspect the result or diff
8. widen scope only if evidence says you need to
```

The order matters. Reading everything first is easy to implement and scales badly.

## Search tactics

Search by **specific evidence**, not by vague concepts.

Good first queries:

- an exception message copied from a failing test
- a function/class name from the stack trace
- a route path such as `/api/users`
- a config key
- a UI string the user can see
- a filename hinted at by an import

Weak first queries:

- `bug`
- `auth stuff`
- `frontend`
- `important code`

If the first search is broad, use the results to derive a narrower second query.

## Reading tactics

A search hit is a pointer, not proof. Read the file before editing it.

When a file is long, ask:

- What symbol did the hit land on?
- What imports does it depend on?
- What calls it?
- What invariant does the surrounding code assume?

Do not keep reopening the same unchanged file. Later context-management chapters will make this explicit.

## Editing tactics

Prefer the smallest change that can falsify your hypothesis.

Bad pattern:

```text
"I found an auth bug, so I reorganized the entire auth module."
```

Better pattern:

```text
"The failing branch compares an ID as int vs str. Change that comparison, then rerun the one failing test."
```

Small edits make verification and rollback cheaper.

## Verification ladder

Use the narrowest check that can prove the change, then widen only when useful:

```text
single function / script
→ one test
→ one test file
→ affected package
→ full test suite
```

A successful command is evidence only for what that command actually checked.

## When the agent loops

If it repeats tools without progress, inspect which of these is missing:

1. **No new observation** — it keeps rereading the same files.
2. **No explicit hypothesis** — actions are not trying to prove anything.
3. **No stop condition** — success is not defined.
4. **Too much context** — the relevant signal is buried.
5. **Tool error is being ignored** — the trace contains the answer but the model did not react.

The fix is usually not "use a bigger model". Tighten the loop first.

## A useful trace should be boring

For a small code task, a good trace often looks like this:

```text
search_code("format_user")
read_file("services/users.py")
write_file("services/users.py", ...)
run_command("pytest tests/test_users.py -q")
git_diff()
final answer
```

Ten speculative tool calls are not more agentic than five evidence-driven ones.

## What to record while experimenting

When you compare agent changes, record at least:

- success/failure
- tool call count
- files read
- files modified
- command count
- model calls
- approximate input/output tokens
- whether verification actually ran
- whether unrelated edits appeared

This becomes the foundation of chapter 15 evals.

## Rule of thumb

**Observe before acting. Verify after acting. Compress only what you can reconstruct. Automate only what you can bound.**
