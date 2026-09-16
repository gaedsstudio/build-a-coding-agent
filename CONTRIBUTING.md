# Contributing

Thanks for helping make coding agents easier to understand.

## Principles

A contribution should preserve the teaching style of this repository:

- keep examples small
- prefer standard-library code when practical
- explain the reason for a new abstraction
- avoid hiding the agent loop behind a framework
- add tests for security boundaries and tricky behavior

## Pull requests

Please keep one conceptual change per pull request.

For a new chapter:

1. Add a focused `README.md`.
2. Include a runnable example.
3. Explain what the chapter intentionally does **not** solve yet.
4. Add at least one test when the chapter introduces a boundary or parser.
5. Update the course table in the root README.

## Security

Tutorial code that executes model-selected actions deserves extra scrutiny.

Never commit API keys, tokens, private repository contents, or credentials.
