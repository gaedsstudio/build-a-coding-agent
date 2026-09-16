# 08 — Git Diff

The agent can plan an edit, but a full file read is a poor way to answer the most important post-edit question:

> **What actually changed?**

This chapter promotes the Git diff to a first-class observation.

## New tool

```text
git_diff(path=".", max_chars=30000)
```

It returns a bounded unified diff for tracked changes inside the workspace.

## Why this matters

After `write_file`, the model may remember what it *intended* to write. That is not evidence of what changed. A diff gives a compact view of additions, removals, and accidental edits.

The healthy sequence becomes:

```text
search / read
→ edit
→ git_diff
→ verify
→ explain
```

## Mission

Change the user prefix from `User:` to `Member:`. Then inspect the diff before running the verification command.

A good diff should make the change obvious without rereading the entire file.

## Checkpoint

You cleared this chapter when the agent can answer both questions directly from the diff:

1. Which tracked files changed?
2. Which exact lines were added and removed?

## Trap

A final file snapshot hides the shape of the change.

Also note: plain `git diff` does not include untracked files. This chapter intentionally keeps that limitation visible instead of hiding it behind a large Git abstraction.

## Boss challenge

Reject success when the diff contains an unrelated file that was not part of the plan.

## Still missing

We can inspect a bad edit, but we do not yet have a first-class way to restore a checkpoint.

**Next:** 09 — Patch & Rollback.
