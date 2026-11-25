# Benchmarks

Exploratory performance benchmarks live here instead of under the runtime or
the example library.

Benchmark suites:

- `fast/`
  Prepared-eval benchmarks. Parsing and interpreter startup are excluded.
  These are intended to cover elemental operations, representative DSL shapes,
  and cache-sensitive sweep workloads.
- `slow/`
  Budget-frontier benchmarks. These search for the largest sweep scale that
  still fits within a configured wall-clock budget.
- `end_to_end/`
  Fresh-session wall-clock benchmarks. Parsing and interpreter startup are
  included.
- `monte_carlo_comparison/`
  Exploratory exact-vs-sampling comparisons for larger workloads.
- `exploratory/`
  One-off scaling probes and plots that reuse the benchmark workload builders
  but are not intended to be stable tracked benchmarks.

Current Monte Carlo comparison workloads:

- `monte_carlo_comparison/hexed_scorching_ray`
  A deep D&D damage sweep used to compare the exact `dice` runtime against
  Monte Carlo implementations.
- `monte_carlo_comparison/chaos_bolt_chain`
  A bounded multi-target Chaos Bolt cascade with repeated attack rolls,
  conditional jumps, and deeper roll-dependent stop logic. This runner now
  times three exact variants before the Monte Carlo backends:
  the naive DSL program, a reduced-state DSL program, and a host-function
  implementation that exercises per-call host caching.

The Monte Carlo comparison runners are exploratory. They may reuse the shared
benchmark helpers, but their report artifacts are local-only and should not be
checked in.

## Reports

All suites can write JSON plus Markdown reports.

- `benchmarks/results/local/`
  Development runs. Gitignored by default.
- `benchmarks/results/tracked/`
  Deliberate checked-in baselines.

Each run writes:

- a JSON artifact for later machine processing
- a Markdown artifact for quick human inspection

Local runs are intended for development-time comparison against tracked
baselines without creating benchmark churn in the repository.

## Commands

Run these from the repository root:

```bash
python3 benchmarks/fast/run.py
```

```bash
python3 benchmarks/slow/run.py
```

```bash
python3 benchmarks/end_to_end/run.py
```

```bash
python3 benchmarks/monte_carlo_comparison/hexed_scorching_ray/run.py
```

```bash
python3 benchmarks/monte_carlo_comparison/chaos_bolt_chain/run.py
```

```bash
python3 benchmarks/exploratory/run.py
```

Notes:

- These benchmarks are exploratory and are not part of the shipped module
  surface.
- The pre-commit hook now benchmarks the staged tree, not unstaged working-tree
  edits. It always runs `fast/` and `end_to_end/` and writes tracked artifacts
  marked `during-commit`.
- Optional commit-time suites:
  `BENCHMARK_SLOW=1 git commit`
  and
  `BENCHMARK_SLOW=1 BENCHMARK_MONTE_CARLO=1 git commit`
- `fast/`, `slow/`, and `end_to_end/` may write `local/` or `tracked/`
  artifacts depending on `--output`.
- The Monte Carlo comparison runners write local report artifacts under
  `benchmarks/results/local/` by default so development runs are easy to
  compare without creating tracked benchmark churn.
- If you do not want report artifacts for a run, pass `--output none`.
- The NumPy backend still rolls primitive dice directly. It does not use
  precomputed alias tables, PMFs, or other derived stochastic primitives.
- The NumPy backend can split each state's trial count evenly across worker
  processes with `--numpy-processes N`.
- The Chaos Bolt runner now benchmarks preset-based full sweeps generated from
  Python. The default preset is `comparison`, which is intended to be large
  enough to be performance-relevant without turning the default comparison into
  a multi-minute run. Use `--preset small` or `--preset medium` when iterating,
  and move up to `--preset large` only when you intentionally want a much
  harder branch-heavy benchmark.
