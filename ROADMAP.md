# Roadmap

The roadmap is intentionally sequential: each chapter introduces a failure mode that motivates the next layer.

> For the full mission/checkpoint/boss-challenge version, use **[docs/ROADMAP_GUIDE.md](./docs/ROADMAP_GUIDE.md)**.

## v0.1 — Build the loop

- [x] 00 — direct model call
- [x] 01 — conversation state
- [x] 02 — native tool calls
- [x] 03 — workspace filesystem
- [x] 04 — constrained command execution

## v0.2 — Understand a repository

- [x] 05 — code search with bounded results
- [x] 06 — bounded context window
- [x] approximate context budget report
- [x] pinned task + recent complete tool turns

## v0.3 — Edit with evidence

- [x] 07 — revisable planning
- [x] 08 — Git diff observation
- [ ] 09 — patch application and rollback ← **next**
- [ ] test/fix loop

## v0.4 — Control execution

- [ ] 10 — execution sandbox
- [ ] 11 — permission levels and approval gates
- [ ] audit trail

## v0.5 — Scale the agent

- [ ] 12 — focused subagents
- [ ] 13 — reusable skills
- [ ] 14 — context compression
- [ ] 15 — eval harness and benchmark tasks

## v1.0 — Full educational coding agent

- [ ] 16 — end-to-end reference implementation
- [ ] architecture/failure-mode guide
- [ ] provider adapters
- [ ] reproducible eval results

## Rule for marking a box complete

A chapter is complete only when:

1. the example runs,
2. its boundary has a test,
3. the README explains the failure mode,
4. the checkpoint can be demonstrated without hand-waving.
