# 07 — Planning

The agent now knows how to search a repository and keep its history bounded. But it still tends to work **opportunistically**: see something, act, see something else, act again.

This chapter adds explicit, mutable plan state.

## New tools

```text
set_plan(steps, reason="")
update_plan_step(index, status, evidence="")
```

The plan lives outside raw chat history and is injected into every model call as current state.

That distinction matters: **a plan is state, not prose buried somewhere in an old assistant message.**

## Rules

- multi-step work should create a 2–6 step plan before editing
- each step has `pending`, `in_progress`, `done`, or `blocked`
- a `done` step requires concrete evidence
- calling `set_plan` again revises the plan instead of pretending the first plan was perfect

## Mission

Run:

```bash
python agent.py
```

Try:

> Find where users are formatted, change `User:` to `Member:`, and verify the change.

A healthy trace might look like:

```text
set_plan(["locate user formatting code", "edit the smallest relevant file", "run a focused verification"])
→ search_code(...)
→ update_plan_step(0, "done", "services/users.py contains format_user")
→ read_file(...)
→ write_file(...)
→ update_plan_step(1, "done", "write_file succeeded")
→ run_command(...)
→ update_plan_step(2, "done", "verification exited 0")
```

## Checkpoint

You cleared this chapter when the agent can **change its plan after new evidence** instead of continuing a stale plan.

## Trap

The first plan is not a contract.

Planning helps coordination, but a bad plan followed perfectly is still bad. Tool results must be allowed to change the plan.

## Boss challenge

Preserve completed steps across a revision instead of replacing the whole plan.

## Still missing

The plan knows what the agent intends to do, but after an edit the agent still lacks a compact first-class view of **what actually changed**.

**Next:** 08 — Git Diff.
