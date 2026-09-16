# 05 — Code Search

The agent can already list files, read files, edit files, and run commands. The next problem is **finding the right code without reading the whole repository**.

This chapter adds one tool:

```text
search_code(query, path=".", max_results=40)
```

## Why this matters

A naive agent can call `list_files`, then open files one by one. That works on toy projects and collapses on real repositories. Search is the first step toward **selective context**.

The implementation deliberately stays simple:

- skips noisy dependency/cache directories
- searches paths and UTF-8 source text
- includes line numbers and compact snippets
- ranks path and token-like matches above broad substrings
- caps result count before tool output reaches the model

## Mission

Run:

```bash
python agent.py
```

Try:

> Find where users are formatted, change the output prefix from `User:` to `Member:`, and verify the result.

A sensible trace is:

```text
search_code("format_user")
→ read_file("services/users.py")
→ write_file("services/users.py", ...)
→ run_command("python app.py") or another suitable check
```

## Checkpoint

You have completed this chapter when you can explain why **search results are observations, not context themselves**. Search should tell the agent what deserves a closer read.

## Boss challenge

Add one of these without changing the public tool schema:

1. respect `.gitignore`
2. rank definitions above call sites
3. add a surrounding-line preview
4. detect obviously binary files without relying on suffixes

## Still missing

Search can find candidate files, but the agent still has no explicit token budget or context-selection policy. That is chapter 06.

**Next:** [06 — Context Management](../docs/ROADMAP_GUIDE.md#06--context-management)
