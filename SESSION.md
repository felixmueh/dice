# Document Title

- Your user facing documentation included a lot of implementation details
 - This is not helpful.


# Package layout (2026-11-25)

- The CLI crashes on a sweep of plain Python ints: `python3 -m dice --file examples/02_python_extensions/00_import_python_library.dice` (and `add_two([1..3])` after importing `basic_library.py`) raise `AttributeError: 'int' object has no attribute 'items'` in `cli._is_deterministic_distribution`. Same on master with `python3 dice.py`; the tests only go through `interpret_*`, not the CLI text formatter.
- `dice/cli.py` holds both the embedding API (`DiceSession`, `dice_interpreter`, `interpret_*`) and the CLI/REPL formatting; splitting the API into its own module would make `dice/__init__.py` independent of the CLI.
- `scripts/generate_render_gallery.py` lists files under `samples/dnd/`, which no longer exists.
- `benchmarks/README.md` gives absolute paths under `/home/felix/_Documents/Projects/dice/`.
