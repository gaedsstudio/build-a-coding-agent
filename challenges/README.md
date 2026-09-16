# Challenges

Use these after completing the matching chapter. They are intentionally underspecified: the point is to make you choose an implementation boundary.

| Level | Challenge | Chapters |
| --- | --- | --- |
| 1 | Add `/reset` without restarting the process | 01 |
| 2 | Add a second safe tool without changing the loop | 02 |
| 3 | Reject symlink-based workspace escapes | 03 |
| 4 | Add per-command timeouts and output budgets | 04 |
| 5 | Respect `.gitignore` in code search | 05 |
| 6 | Pin one important observation so it survives normal context eviction | 06 |
| 7 | Preserve completed steps across a plan revision | 07 |
| 8 | Summarize a diff without rereading changed files | 08 |
| 9 | Roll back one bad file but keep a good edit | 09 |
| 10 | Enforce CPU/time/filesystem limits in isolation | 10 |
| 11 | Add session-scoped approvals | 11 |
| 12 | Delegate two investigations with restricted tools | 12 |
| 13 | Build a reusable debugging skill | 13 |
| 14 | Test whether compression preserves five facts | 14 |
| 15 | Compare two agent versions on the same benchmark | 15 |
| 16 | Fix an unfamiliar repo end-to-end | 16 |

For each challenge, write down the failure mode you are trying to prevent **before** writing code. If you cannot state the failure mode, the abstraction is probably premature.
