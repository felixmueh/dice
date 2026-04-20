# Slow Benchmarks: Budget Frontier

## Run Metadata

- timestamp: 2026-04-20T21:51:15+02:00
- git commit: None
- git branch: None
- run context: during-commit
- worktree dirty: no
- host: fedora.fritz.box
- platform: Linux-6.19.11-200.fc43.x86_64-x86_64-with-glibc2.42
- python: 3.14.3

## Configuration

- budget (s): 1.00
- timed samples per candidate: 1
- warmup samples per candidate: 0
- parsing included: no
- interpreter startup included: no
- cache mode: cold

## Results

| Benchmark                    | Budget (s) | Frontier Cells | Frontier Point                                            | Frontier Median (s) | Stdev (s) | StdErr Mean (s) | First Fail                                                |
| ---------------------------- | ---------- | -------------- | --------------------------------------------------------- | ------------------- | --------- | --------------- | --------------------------------------------------------- |
| Damage Sweep Frontier        | 1.00       | 640            | ac=64 repeats=10 cells=640                                | 0.022               | 0.000     | 0.000           | -                                                         |
| Hexed Scorching Ray Frontier | 1.00       | 2016           | slots=7 modes=3 attacks=3 bless=2 ac=16 cells=2016        | 0.713               | 0.000     | 0.000           | -                                                         |
| Chaos Bolt Chain Frontier    | 1.00       | 64             | slots=2 modes=2 attacks=2 bless=1 targets=2 ac=4 cells=64 | 0.645               | 0.000     | 0.000           | slots=2 modes=2 attacks=2 bless=2 targets=1 ac=4 cells=64 |
