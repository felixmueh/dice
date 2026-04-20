# Monte Carlo Comparison: Hexed/Blessed Scorching Ray

- Axis order: SLOT, MODE, ATTACK, BLESS, AC
- Timing scope: full exact sweep across 1,260 cells
- Sample counts: baseline=4,000 numpy=4,000, 32,000
- NumPy config: processes=16 batch_size=50,000

## Run Metadata

- timestamp: 2026-04-20T21:51:51+02:00
- git commit: None
- git branch: None
- run context: during-commit
- worktree dirty: no
- host: fedora.fritz.box
- platform: Linux-6.19.11-200.fc43.x86_64-x86_64-with-glibc2.42
- python: 3.14.3

## Current Results

| Backend                      | Samples / cell | Scope                    | Time (s) | Stdev (s) | StdErr Mean (s) | vs dice | Rep. mean abs err |
| ---------------------------- | -------------- | ------------------------ | -------- | --------- | --------------- | ------- | ----------------- |
| dice exact                   | -              | full sweep (1,260 cells) | 0.522    | 0.000     | 0.000           | 1.00x   | 0.0000            |
| Naive Python Monte Carlo     | 4,000          | full sweep (1,260 cells) | 33.547   | 0.000     | 0.000           | 64.30x  | 0.2184            |
| Vectorized NumPy Monte Carlo | 4,000          | full sweep (1,260 cells) | 0.384    | 0.000     | 0.000           | 0.74x   | 0.2923            |
| Vectorized NumPy Monte Carlo | 32,000         | full sweep (1,260 cells) | 0.700    | 0.000     | 0.000           | 1.34x   | 0.0861            |

## Representative Cells

### baseline 4,000

- (2, 'normal', 7, 0, 13) exact_mean=34.200 sampled_mean=34.085 exact_support=115 sampled_support=67
- (5, 'advantage', 9, 1, 17) exact_mean=88.466 sampled_mean=88.297 exact_support=235 sampled_support=91
- (8, 'elven_accuracy', 11, 1, 22) exact_mean=136.637 sampled_mean=137.008 exact_support=355 sampled_support=112

### numpy 4,000

- (2, 'normal', 7, 0, 13) exact_mean=34.200 sampled_mean=34.629 exact_support=115 sampled_support=67
- (5, 'advantage', 9, 1, 17) exact_mean=88.466 sampled_mean=88.178 exact_support=235 sampled_support=95
- (8, 'elven_accuracy', 11, 1, 22) exact_mean=136.637 sampled_mean=136.797 exact_support=355 sampled_support=120

### numpy 32,000

- (2, 'normal', 7, 0, 13) exact_mean=34.200 sampled_mean=34.187 exact_support=115 sampled_support=76
- (5, 'advantage', 9, 1, 17) exact_mean=88.466 sampled_mean=88.278 exact_support=235 sampled_support=116
- (8, 'elven_accuracy', 11, 1, 22) exact_mean=136.637 sampled_mean=136.694 exact_support=355 sampled_support=139
