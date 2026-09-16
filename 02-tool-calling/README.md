# 02 — Tool calling

The model can now request an action instead of only producing text.

We start with a deliberately boring calculator because the important lesson is the protocol:

```text
model → tool request → executor → tool result → model
```

The executor owns the real capability. The model only asks.

## Run

```bash
python agent.py
```

Try:

> What is (1847 * 29) + 913?
