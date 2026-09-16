# 03 — Filesystem tools

A coding agent becomes useful when it can inspect and change code.

This chapter adds:

- `list_files`
- `read_file`
- `write_file`

All paths are resolved beneath `workspace/`.

## The first real safety boundary

Never trust a model-generated path.

`../../secrets.txt` must not escape the workspace. The executor resolves every requested path and rejects anything outside the workspace root.

## Run

```bash
python agent.py
```

Try:

> Read the project and add a `greet(name)` function to `hello.py`.

Then inspect `workspace/hello.py`.
