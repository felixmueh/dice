# Benchmark Results

Benchmark artifacts are split into two classes:

- `tracked/`
  Intended for deliberate, checked-in benchmark baselines.
- `local/`
  Development-time runs. This directory is gitignored and should not be
  checked in.

The Monte Carlo comparison benchmarks currently only write `local/` artifacts.
Commit-time runs are the exception: the pre-commit hook may write tracked
Monte Carlo artifacts when `BENCHMARK_MONTE_CARLO=1` is set.

Each output directory may also contain `latest.md`, an automatically generated
combined report for all JSON artifacts present in that output mode.
