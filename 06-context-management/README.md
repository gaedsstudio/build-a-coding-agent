# 06 — Context Management

Search solved **where should I look?** This chapter tackles the next problem:

> How much of what I already saw should I keep sending back to the model?

A coding agent can produce a long trace very quickly: searches, file reads, command output, errors, retries, and edits. Sending all of it forever is expensive and eventually impossible.

This chapter adds a bounded `ContextWindow`.

## What changes

The agent now keeps:

- the system prompt
- the original user task
- the newest complete tool exchanges that still fit the budget

Older exchanges fall out first.

A tool-call message and its tool results are treated as **one atomic turn**. We never keep a tool result while dropping the assistant message that requested it.

The token count is an approximation (`~4 chars/token`) on purpose. Exact tokenization is provider-specific; the engineering idea is the budget.

## Run

```bash
python agent.py
```

Optional debug mode:

```bash
AGENT_CONTEXT_DEBUG=1 AGENT_CONTEXT_TOKENS=3000 python agent.py
```

PowerShell:

```powershell
$env:AGENT_CONTEXT_DEBUG="1"
$env:AGENT_CONTEXT_TOKENS="3000"
python agent.py
```

You will see lines like:

```text
[context] context≈1840/3000 tokens | kept_turns=4 | dropped_turns=2
```

## Mission

Give the agent a task that requires several searches and reads, then run it again with a much smaller `AGENT_CONTEXT_TOKENS` value.

Watch which evidence disappears first.

## Checkpoint

You cleared this chapter when you can explain all three:

1. why the system prompt and original task are pinned
2. why tool calls and tool results must be dropped together
3. why dropping old raw traces is different from summarizing them

## Trap

A context window is **not memory**.

This chapter only decides what raw history remains visible. When important old facts need to survive after their raw trace is gone, we need explicit compression or memory. That comes later.

## Boss challenge

Add one of these:

- pin a specific observation so it survives normal eviction
- reserve a separate budget for command output
- show which exact turns were evicted
- replace the rough estimator with a provider-specific tokenizer adapter

## Still missing

The agent can now bound history, but it still executes opportunistically.

Next we separate **deciding the steps** from **performing them**.

**Next:** [07 — Planning](../docs/ROADMAP_GUIDE.md#07--planning)
