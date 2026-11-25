# AGENTS

## Project Overview

`dice` is a Python language for exact and sampled tabletop probability calculations. The active runtime is the parser/interpreter/engine stack plus the CLI in `dice.py`, with user-facing semantics documented in `README.md`, `manual/`, and `examples/`.

## Where To Look

- `README.md`: shortest user-facing quickstart and tested core semantics
- `manual/`: canonical long-form user-facing manual and MkDocs source
- `examples/`: user-facing sample programs, including D&D and Python-extension examples
- `agent-notes/README.md`: internal map of architecture, design notes, research, and backlog
- `lexer.py` -> `diceparser.py` -> `syntaxtree.py` -> `interpreter.py` -> `diceengine.py`: core language pipeline
- `executor.py`: builtin registration and executor surface shared by dice and Python
- `viewer.py`, `renderplan.py`, `jsonrenderer.py`, `resultjson.py`: report planning and rendering
- `tests/`: executable contract, especially `tests/test_readme_examples.py` and `tests/test_manual_examples.py`

## Important Rules

- Treat `README.md`, `manual/`, `examples/`, and the tests as the current contract.
- For syntax changes, update `lexer.py`, `diceparser.py`, and `interpreter.py` together.
- For semantic changes, check `diceengine.py` first. Most exact operator and callable behavior lives there.
- When adding builtins, define the behavior in `diceengine.py` and register it through `executor.py` so dice and Python share one callable surface.
- Keep imports explicit and runtime-visible. Resolve relative imports from the importing file; do not reintroduce hidden preprocessing behavior by accident.
- Keep fenced `dice` examples in `README.md` and `manual/` executable, or update the runtime and tests in the same change.
- Add end-to-end tests for semantic changes where practical.

## Secondary Rules

- Prefer pointing agents to user-facing docs instead of duplicating semantics in `agent-notes/`. Keep internal notes shorter unless extra implementation detail is genuinely useful.
- Multiline functions are part of the active language surface; prefer them over dense one-line helpers when examples need local bindings or repeated subexpressions.
- Use `==` for singleton exact checks such as `d20 == 20`, ordinary comparisons for thresholds such as `d20 >= 15`, and `in` for genuine membership checks such as `d20 in {1, 20}`.
- `notes.org` and `scripts/` are useful for history and intent, but they are not guaranteed to match the active runtime.
- `dnd-sources/` is local development/reference material only. Do not quote or surface it in user-facing docs, tests, or examples unless explicitly asked.
- Record agent observations in `agent-notes/backlog/language-observations-and-painpoints.md`.
- For performance-sensitive work, consult `benchmarks/README.md` and the notes under `agent-notes/design/`. Normal `git commit` already runs the staged-tree `fast/` and `end_to_end/` suites via `.githooks/pre-commit`.
