# Roadmap Guide

This is the playable version of the roadmap.

Every chapter has five parts:

- **Goal** — the engineering idea you are learning.
- **Build** — the smallest capability you add.
- **Clear condition** — what must be true before you move on.
- **Trap** — the mistake this chapter is designed to expose.
- **Boss challenge** — an optional extension that forces the idea to stick.

Do not rush to chapter 16. The point of this repository is to understand **why each layer exists**.

---

## 00 — Hello Agent

**Goal:** Cross the model API boundary without hiding it behind a framework.

**Build:** One system message, one user message, one response.

**Clear condition:** You can point to the exact JSON that leaves your program and the exact model message that comes back.

**Trap:** Calling a model and calling that an "agent". There is no action loop yet.

**Boss challenge:** Log request latency and response size without changing model behavior.

[Open chapter →](../00-hello-agent/)

## 01 — Agent Loop

**Goal:** Understand state and stopping conditions.

**Build:** Persistent messages inside a terminal session.

**Clear condition:** A second user turn can rely on information from the first turn.

**Trap:** Infinite loops and unbounded message growth.

**Boss challenge:** Add `/reset` and show exactly which messages are discarded.

[Open chapter →](../01-agent-loop/)

## 02 — Tool Calling

**Goal:** Separate model intent from program authority.

**Build:** A model → tool request → executor → tool result → model loop.

**Clear condition:** The model can request arithmetic, but your code still decides what is actually executed.

**Trap:** Treating tool arguments as trusted input.

**Boss challenge:** Add a second harmless tool and route both through one executor.

[Open chapter →](../02-tool-calling/)

## 03 — Filesystem

**Goal:** Give the agent useful power without giving it your whole machine.

**Build:** `list_files`, `read_file`, and `write_file` scoped to `workspace/`.

**Clear condition:** `../secret.txt` is rejected and normal nested files still work.

**Trap:** String-prefix path checks. Resolve paths first, then prove they remain under the workspace root.

**Boss challenge:** Add a file-size limit and a clear error for binary files.

[Open chapter →](../03-filesystem/)

## 04 — Shell Execution

**Goal:** Turn edits into evidence by running development commands.

**Build:** A constrained `run_command` tool with no shell interpolation, an executable allowlist, timeout, and output cap.

**Clear condition:** `python demo.py` works while an unlisted executable is rejected.

**Trap:** `shell=True` with model-generated strings.

**Boss challenge:** Add per-command timeout defaults and explain why this is still not a real sandbox.

[Open chapter →](../04-shell-execution/)

## 05 — Code Search

**Goal:** Find relevant code without reading the repository file-by-file.

**Build:** `search_code(query, path, max_results)` with path matches, line numbers, snippets, directory skips, ranking, and result caps.

**Clear condition:** Given a symbol name, the agent searches first and reads only the likely files.

**Trap:** Dumping thousands of search matches into context. Search narrows the field; it does not replace reading.

**Boss challenge:** Respect `.gitignore`, rank definitions above references, or show surrounding lines.

[Open chapter →](../05-code-search/)

## 06 — Context Management

**Goal:** Spend context on information that can change the next decision.

**Build:** A context selector that tracks candidates, recent observations, pinned files, and an explicit size budget.

**Clear condition:** A task on one module does not cause unrelated files to be repeatedly re-sent to the model.

**Trap:** "More context is always better." Irrelevant context raises cost and can lower decision quality.

**Boss challenge:** Print a context budget report before every model call.

## 07 — Planning

**Goal:** Separate deciding what to do from doing it.

**Build:** A short mutable plan with steps, status, and a reason to revise.

**Clear condition:** The agent can abandon a bad plan after new tool evidence arrives.

**Trap:** Treating the first plan as a contract.

**Boss challenge:** Require every plan step to name the evidence that will mark it complete.

## 08 — Git Diff

**Goal:** Make code changes inspectable as changes, not just final file contents.

**Build:** A `git_diff` observation and a compact diff summary.

**Clear condition:** Before claiming success, the agent can explain exactly what changed.

**Trap:** Re-reading whole files when the important observation is the patch.

**Boss challenge:** Detect accidental unrelated edits from the diff.

## 09 — Patch & Rollback

**Goal:** Make edits reversible.

**Build:** Patch application plus a checkpoint/rollback mechanism.

**Clear condition:** A failed edit can be reverted without reconstructing old files from memory.

**Trap:** Letting the model "undo" by generating another full file replacement.

**Boss challenge:** Roll back only one file while preserving another successful edit.

## 10 — Sandbox

**Goal:** Isolate execution from the host environment.

**Build:** Run commands in a disposable isolated workspace with explicit mounts/resources.

**Clear condition:** The agent cannot modify files outside the mounted project boundary through command execution.

**Trap:** Confusing an allowlist with isolation.

**Boss challenge:** Add CPU/time/output limits and show the failure mode for each.

## 11 — Permissions

**Goal:** Decide which actions may happen automatically and which need human approval.

**Build:** Permission classes such as `read`, `edit`, `execute`, and `external` with approval gates.

**Clear condition:** A task can continue automatically through safe reads while pausing on a protected action.

**Trap:** One global "safe mode" toggle.

**Boss challenge:** Add session-scoped approvals: "allow this exact command for the rest of this run."

## 12 — Subagents

**Goal:** Delegate narrow work without losing control of the main task.

**Build:** Focused child runs with limited context, tools, and a structured return value.

**Clear condition:** A child agent can investigate one question and return evidence without inheriting the whole conversation.

**Trap:** Spawning more agents instead of improving decomposition.

**Boss challenge:** Run two independent investigations and merge only their evidence summaries.

## 13 — Agent Skills

**Goal:** Package reusable workflows outside the core loop.

**Build:** Loadable skill folders with instructions, examples, and optional resources.

**Clear condition:** Adding a new workflow does not require editing the central agent loop.

**Trap:** Turning every prompt fragment into a "skill".

**Boss challenge:** Create a debugging skill with an eval that shows it improves a repeatable task.

## 14 — Context Compression

**Goal:** Keep long sessions useful after raw history becomes too large.

**Build:** Summaries that preserve decisions, open questions, file state, and verification evidence.

**Clear condition:** After compression, the agent can continue the task without redoing already-settled work.

**Trap:** Generic prose summaries that erase concrete filenames, commands, and decisions.

**Boss challenge:** Compress a long trace, then compare answers before and after compression on five factual questions.

## 15 — Evals

**Goal:** Replace "this feels smarter" with repeatable measurements.

**Build:** A small benchmark of repository tasks with success checks, traces, cost, and step counts.

**Clear condition:** A code change to the agent can be compared against a previous version on the same tasks.

**Trap:** Using only model-graded vibes as the success criterion.

**Boss challenge:** Add one eval where a more verbose agent performs worse because it wastes context or tools.

## 16 — Full Agent

**Goal:** Assemble the system while keeping every boundary understandable.

**Build:** Context selection + planning + tools + diffs + rollback + sandbox + permissions + skills + eval instrumentation.

**Clear condition:** You can trace a real task from user request to final verified patch and explain which chapter owns each part of the flow.

**Trap:** Refactoring everything into abstractions until the educational value disappears.

**Boss challenge:** Give the agent an unfamiliar small repository and fix a bug using only the interfaces built in this course.

---

## Recommended pace

A good rhythm is **one chapter, one modification, one failure you can explain**. If you finish a chapter but cannot explain its trap, repeat the boss challenge before moving on.
