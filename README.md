<p align="center">
  <img src="./assets/hero.svg" alt="Build a Coding Agent From Scratch" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/gaedsstudio/build-a-coding-agent/actions/workflows/tests.yml"><img alt="tests" src="https://github.com/gaedsstudio/build-a-coding-agent/actions/workflows/tests.yml/badge.svg" /></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-161B22?logo=python&logoColor=58A6FF" />
  <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-161B22" />
</p>

<p align="center">
  <strong>Build the loop, not the wrapper.</strong><br />
  A step-by-step course for understanding coding agents by implementing the machinery yourself.
</p>

<p align="center">
  <a href="#start-here">Start here</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#course">Course</a> ·
  <a href="./ROADMAP.md">Roadmap</a> ·
  <a href="./CONTRIBUTING.md">Contributing</a>
</p>

---

## Why this repository exists

A coding agent can look mysterious when everything arrives at once: model calls, tool schemas, filesystem access, shell execution, code search, planning, context management, permissions, sandboxes, skills, subagents, and evals.

This repository takes the opposite approach.

**Add one capability. Run it. Understand the boundary. Then add the next one.**

There is no agent framework hiding the important parts. The examples intentionally keep the core loop visible so you can see where model output ends and your program's authority begins.

> **No LangChain. No giant abstraction layer. No magic step between “the model asked” and “the machine did it.”**

By the end, you will have a small but real coding agent that can inspect a repository, change files, run development commands, evaluate results, and iterate on its own work.

## How it works

<p align="center">
  <img src="./assets/architecture.svg" alt="How a coding agent works" width="100%" />
</p>

The central idea is deliberately small:

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

A model does not directly own your filesystem, shell, or Git repository. It produces a **request**. Your executor validates that request, performs an allowed action, and feeds evidence back into the loop.

That separation is what later chapters build on for safer execution, permissions, rollback, context management, and evals.

## Course

<p align="center">
  <img src="./assets/roadmap.svg" alt="Build a Coding Agent learning roadmap" width="100%" />
</p>

The first five chapters are implemented today. `05-code-search` is next.

| Chapter | What you build | Status |
| --- | --- | :---: |
| [`00-hello-agent`](./00-hello-agent) | The smallest useful model call | ✅ |
| [`01-agent-loop`](./01-agent-loop) | Persistent conversation state and a stop condition | ✅ |
| [`02-tool-calling`](./02-tool-calling) | A real model → tool → result loop | ✅ |
| [`03-filesystem`](./03-filesystem) | Workspace-scoped file listing, reading, and writing | ✅ |
| [`04-shell-execution`](./04-shell-execution) | Constrained development command execution | ✅ |
| `05-code-search` | Find relevant code without reading the whole repository | 🚧 |
| `06-context-management` | Spend context on the files that matter | planned |
| `07-planning` | Separate planning from execution | planned |
| `08-git-diff` | Inspect and reason about changes | planned |
| `09-patch-and-rollback` | Make edits reversible | planned |
| `10-sandbox` | Isolate dangerous operations | planned |
| `11-permissions` | Add explicit approval boundaries | planned |
| `12-subagents` | Delegate focused tasks | planned |
| `13-agent-skills` | Load reusable domain workflows | planned |
| `14-context-compression` | Keep long-running sessions useful | planned |
| `15-evals` | Measure whether the agent is actually improving | planned |
| `16-full-agent` | Put the system together | planned |

Each chapter is a standalone checkpoint. You should be able to read the diff from the previous chapter and understand **why that extra machinery now exists**.

## Start here

### 1. Requirements

- Python 3.11+
- An OpenAI-compatible chat-completions endpoint
- An API key for that endpoint

This tutorial talks to the HTTP API directly with the Python standard library. That is intentional: fewer dependencies means fewer important details disappear behind a client framework.

### 2. Configure a model

macOS / Linux:

```bash
export AGENT_API_KEY="..."
export AGENT_MODEL="your-model"
export AGENT_BASE_URL="https://api.openai.com/v1"  # optional
```

PowerShell:

```powershell
$env:AGENT_API_KEY="..."
$env:AGENT_MODEL="your-model"
$env:AGENT_BASE_URL="https://api.openai.com/v1"   # optional
```

### 3. Run chapter 00

```bash
git clone https://github.com/gaedsstudio/build-a-coding-agent.git
cd build-a-coding-agent/00-hello-agent
python agent.py
```

Then move forward one chapter at a time.

## What changes as the agent grows

| Early tutorial | Later system |
| --- | --- |
| A list of messages | Token-aware context selection |
| A few hard-coded tools | A permissioned tool router |
| Direct file replacement | Patches, diffs, and rollback |
| Local command allowlist | Isolated execution sandbox |
| One loop | Plans, skills, and focused subagents |
| “It seems to work” | Reproducible eval tasks |

The code grows because the **failure modes** grow. Every abstraction in the later chapters should be traceable back to a concrete problem you already saw in a smaller version.

## Design principles

1. **Small chapters.** One important engineering idea at a time.
2. **Visible machinery.** Avoid abstractions until they earn their place.
3. **Working checkpoints.** Every implemented chapter should run on its own.
4. **Bound capabilities.** Model-selected actions are validated by ordinary code.
5. **Provider-light concepts.** The architecture should survive model and API changes.
6. **Production ideas, educational implementation.** The repository explains real failure modes without pretending a tutorial workspace is a hardened sandbox.

## Repository layout

```text
.
├── 00-hello-agent/
├── 01-agent-loop/
├── 02-tool-calling/
├── 03-filesystem/
├── 04-shell-execution/
├── assets/
│   ├── architecture.svg
│   ├── hero.svg
│   └── roadmap.svg
├── docs/
│   └── architecture.md
├── skills/
│   └── README.md
├── tests/
├── CONTRIBUTING.md
├── ROADMAP.md
└── README.md
```

## What this is not

This is not a clone of Cursor, Claude Code, Codex, or any other coding product.

It is an educational implementation of the general engineering ideas behind tool-using coding agents.

## Contributing

The most useful contributions make one part of the system easier to understand: a clearer explanation, a smaller implementation, a real edge case, a stronger boundary test, a better eval, or a reusable skill example.

See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## License

MIT.
