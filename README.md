# Build a Coding Agent From Scratch

> Learn how coding agents work by building one yourself — from a single LLM call to filesystem tools, shell execution, context management, sandboxing, skills, subagents, and evals.

**No LangChain. No agent framework. No magic.**

This repository is a step-by-step course disguised as a codebase. Every chapter is small enough to read, run, break, and rebuild.

## Why this exists

Coding agents look complicated because production systems contain a lot of infrastructure at once:

- model calls
- conversation state
- tool schemas
- filesystem access
- shell execution
- code search
- patching
- context compression
- permission checks
- sandboxes
- planning
- subagents
- skills
- evaluation

The trick is to add them **one at a time**.

By the end, you will have a small but real coding agent that can inspect a repository, edit files, run commands, and iterate on its own work.

## What you will build

```text
User
  │
  ▼
Agent Loop ────────────────┐
  │                        │
  ├── Context Manager      │
  ├── Planner              │
  ├── Skill Loader         │
  │                        │
  ▼                        │
Tool Router                │
  ├── read_file            │
  ├── write_file           │
  ├── search_code          │
  ├── run_command          │
  └── git_diff             │
  │                        │
  ▼                        │
Workspace / Sandbox        │
  │                        │
  └──── results ───────────┘
```

## Course

| Chapter | Build | Status |
|---|---|---|
| `00-hello-agent` | Make the smallest useful model call | ✅ |
| `01-agent-loop` | Add persistent conversation state | ✅ |
| `02-tool-calling` | Let the model call a real tool | ✅ |
| `03-filesystem` | Read and write files inside a workspace | ✅ |
| `04-shell-execution` | Run constrained development commands | ✅ |
| `05-code-search` | Search a repository efficiently | 🚧 |
| `06-context-management` | Stop stuffing the whole repo into context | planned |
| `07-planning` | Separate planning from execution | planned |
| `08-git-diff` | Inspect and reason about patches | planned |
| `09-patch-and-rollback` | Make edits reversible | planned |
| `10-sandbox` | Isolate dangerous operations | planned |
| `11-permissions` | Add human approval boundaries | planned |
| `12-subagents` | Delegate focused tasks | planned |
| `13-agent-skills` | Load reusable domain skills | planned |
| `14-context-compression` | Summarize long-running work | planned |
| `15-evals` | Measure whether the agent is improving | planned |
| `16-full-agent` | Put the pieces together | planned |

## Requirements

- Python 3.11+
- An OpenAI-compatible chat-completions endpoint
- An API key for that endpoint

The tutorial intentionally talks to the HTTP API directly. That keeps the important machinery visible.

Set:

```bash
export AGENT_API_KEY="..."
export AGENT_MODEL="your-model"
```

Optional:

```bash
export AGENT_BASE_URL="https://api.openai.com/v1"
```

On PowerShell:

```powershell
$env:AGENT_API_KEY="..."
$env:AGENT_MODEL="your-model"
$env:AGENT_BASE_URL="https://api.openai.com/v1"
```

## Start here

```bash
cd 00-hello-agent
python agent.py
```

Then move chapter by chapter.

Each chapter contains its own README explaining **what changed, why it matters, and what is still deliberately missing**.

## Design rules

This project follows a few rules:

1. **Small chapters.** A chapter should teach one important idea.
2. **Visible machinery.** Avoid abstractions until they earn their place.
3. **Working code.** Explanations should lead to something you can run.
4. **Safe by construction.** Filesystem paths stay inside a workspace; command execution becomes constrained before it becomes powerful.
5. **Provider-light.** The concepts should survive model/provider changes.
6. **Production ideas, educational implementation.** We explain the real systems without pretending a tutorial sandbox is production security.

## The interesting part is not the prompt

A coding agent is not just:

```python
answer = model("fix my code")
```

The interesting part is the loop:

```python
while True:
    response = model(messages, tools=tools)

    if not response.tool_calls:
        return response.text

    messages.append(response.as_message())

    for call in response.tool_calls:
        result = execute(call)
        messages.append(tool_result(call, result))
```

Everything else in this repository gradually makes that loop more capable, more efficient, and less dangerous.

## Repository layout

```text
.
├── 00-hello-agent/
├── 01-agent-loop/
├── 02-tool-calling/
├── 03-filesystem/
├── 04-shell-execution/
├── docs/
│   └── architecture.md
├── skills/
│   └── README.md
├── tests/
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## What this is not

This is not a clone of Cursor, Claude Code, Codex, or any other product.

It is an educational implementation of the general engineering ideas behind tool-using coding agents.

## Contributing

The best contributions are:

- a clearer explanation
- a smaller implementation
- a failing edge case
- a better safety boundary
- an eval that catches a real regression
- a skill that teaches a reusable workflow

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT.
