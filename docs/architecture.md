# Architecture: what makes a coding agent an agent?

A model can produce code without being an agent.

A coding **agent** gets a feedback loop between reasoning and the environment:

```text
observe → decide → act → observe → ...
```

For code, the environment is usually a repository plus development tools.

## Minimal loop

The smallest useful architecture has four pieces:

1. **Messages** — what the model currently knows.
2. **Tools** — actions the model is allowed to request.
3. **Executor** — code that validates and performs those actions.
4. **Loop** — feeds results back until the model stops requesting actions.

## Why tools are the boundary

The model should not directly possess filesystem or process privileges.

It asks for an action:

```json
{
  "name": "read_file",
  "arguments": {
    "path": "src/app.py"
  }
}
```

Your program decides whether that action is valid.

That distinction becomes critical later when we add permissions and sandboxing.

## The roadmap

Early chapters optimize for understanding.

Later chapters add the properties production agents need:

- bounded context
- reversible edits
- explicit permissions
- isolated execution
- traceability
- evaluation
- reusable skills

The architecture grows because the failure modes grow.
