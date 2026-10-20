# CLAUDE.md

Project: AI Supply Chain Map. The spec is `docs/spec-v1.0.md`, and decisions are logged in `docs/decisions.md`.

## Logic gates (how to ask for decisions)

When a path forward needs my decision, don't write one long answer with a big decision at the end.

- Break the decision into small **gates**, one at a time.
- Each gate gives **three clear options**, labeled A, B and C, readable in about one minute.
- Mark the recommended option.
- Keep each option to one or two lines: what it means and what it leads to.
- When there are several gates, show the path first (numbered list, current gate marked).
- After I pick, lock it in with one line, then move to the next gate.
- I may tweak an option ("A, but ..."); restate it and move on.
- When the gates are done, record the decisions in the project's decision log (`docs/decisions.md`).

## How I like to work

- I code mostly in Python.
- Take things step by step. Break tasks into small, simple steps.
- Don't assume I know how to do everything. Explain commands and what they do.

## Checks before committing

- `python -m pytest`
- `python -m pipeline.validate`
