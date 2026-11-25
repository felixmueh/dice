# AGENTS

## Project Overview

`dice` is a Python language for exact and sampled tabletop probability calculations. The active runtime is the `dice/` package: the parser/interpreter/engine stack plus the CLI in `dice/cli.py` (run as `python3 -m dice`), with user-facing semantics documented in `README.md`, `manual/`, and `examples/`.

## Where To Look

- `README.md`: shortest user-facing quickstart and tested core semantics
- `manual/`: canonical long-form user-facing manual and MkDocs source
- `examples/`: user-facing sample programs, including D&D and Python-extension examples
- `agent-notes/README.md`: internal map of architecture, design notes, research, and backlog
- `dice/__init__.py`: the public Python surface (`from dice import dice_interpreter, dicefunction, ...`); `dice/__main__.py` starts the CLI
- `dice/lexer.py` -> `dice/diceparser.py` -> `dice/syntaxtree.py` -> `dice/interpreter.py` -> `dice/diceengine.py`: core language pipeline
- `dice/executor.py`: builtin registration and executor surface shared by dice and Python
- `dice/viewer.py`, `dice/renderplan.py`, `dice/jsonrenderer.py`, `dice/resultjson.py`: report planning and rendering
- `dice/stdlib/`: the packaged standard library behind `import "std:..."`
- `tests/`: executable contract, especially `tests/test_readme_examples.py` and `tests/test_manual_examples.py`

## Important Rules

- Treat `README.md`, `manual/`, `examples/`, and the tests as the current contract.
- For syntax changes, update `dice/lexer.py`, `dice/diceparser.py`, and `dice/interpreter.py` together.
- For semantic changes, check `dice/diceengine.py` first. Most exact operator and callable behavior lives there.
- When adding builtins, define the behavior in `dice/diceengine.py` and register it through `dice/executor.py` so dice and Python share one callable surface.
- Keep imports explicit and runtime-visible. Resolve relative imports from the importing file; do not reintroduce hidden preprocessing behavior by accident.
- Python modules inside `dice/` import each other relatively (`from .diceengine import ...`); tests, benchmarks and scripts import `dice.<module>`. dice-web vendors the package into Pyodide and swaps in its own `dice/viewer.py`, so keep the matplotlib import confined to `viewer.py`.
- Keep fenced `dice` examples in `README.md` and `manual/` executable, or update the runtime and tests in the same change.
- Add end-to-end tests for semantic changes where practical.

## Secondary Rules

- Prefer pointing agents to user-facing docs instead of duplicating semantics in `agent-notes/`. Keep internal notes shorter unless extra implementation detail is genuinely useful.
- Multiline functions are part of the active language surface; prefer them over dense one-line helpers when examples need local bindings or repeated subexpressions.
- Use `==` for singleton exact checks such as `d20 == 20`, ordinary comparisons for thresholds such as `d20 >= 15`, and `in` for genuine membership checks such as `d20 in {1, 20}`.
- `scripts/` and the local `agent-notes/notes.org` (2020 interpreter-tutorial notes) are useful for history and intent, but they are not guaranteed to match the active runtime.
- `dnd-sources/` is local development/reference material only. Do not quote or surface it in user-facing docs, tests, or examples unless explicitly asked.
- Record agent observations in `agent-notes/backlog/language-observations-and-painpoints.md`.
- For performance-sensitive work, consult `benchmarks/README.md` and the notes under `agent-notes/design/`. Normal `git commit` already runs the staged-tree `fast/` and `end_to_end/` suites via `.githooks/pre-commit`.
