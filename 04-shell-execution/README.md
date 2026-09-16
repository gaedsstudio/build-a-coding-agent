# 04 — Shell execution, without handing over the machine

A useful coding agent needs feedback from tests, formatters, compilers, and Git.

This chapter adds `run_command`, but deliberately **does not** expose an unrestricted shell.

The executor:

- parses arguments without `shell=True`
- permits only a small executable allowlist
- runs inside `workspace/`
- applies a timeout
- truncates large output

This is a teaching boundary, not a real sandbox. Later chapters isolate execution more strongly.

## Run

```bash
python agent.py
```

Try:

> Inspect the code, improve it, then run it with Python to verify your change.
