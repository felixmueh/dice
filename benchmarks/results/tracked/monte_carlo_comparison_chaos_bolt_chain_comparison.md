# Monte Carlo Comparison: Chaos Bolt chain (comparison)

- Preset: comparison
- Axis order: SLOT, MODE, ATTACK, BLESS, TARGETS, AC
- Timing scope: full exact sweep across 1,536 cells
- Sample counts: baseline=4,000 numpy=4,000, 32,000
- NumPy config: processes=16 batch_size=50,000

## Run Metadata

- timestamp: 2026-04-20T21:52:49+02:00
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
| dice exact (naive DSL)       | -              | full sweep (1,536 cells) | 23.957   | 0.000     | 0.000           | 1.00x   | 0.0000            |
| dice exact (delta DSL)       | -              | full sweep (1,536 cells) | 21.128   | 0.000     | 0.000           | 0.88x   | 0.0000            |
| dice exact (host functions)  | -              | full sweep (1,536 cells) | 1.233    | 0.000     | 0.000           | 0.05x   | 0.0000            |
| Naive Python Monte Carlo     | 4,000          | full sweep (1,536 cells) | 10.529   | 0.000     | 0.000           | 0.44x   | 0.1711            |
| Vectorized NumPy Monte Carlo | 4,000          | full sweep (1,536 cells) | 0.488    | 0.000     | 0.000           | 0.02x   | 0.0574            |
| Vectorized NumPy Monte Carlo | 32,000         | full sweep (1,536 cells) | 0.776    | 0.000     | 0.000           | 0.03x   | 0.0506            |

## Representative Cells

### baseline 4,000

- (1, 'normal', 7, 0, 2, 12) exact_mean=11.688 sampled_mean=11.815 exact_support=87 sampled_support=45
- (3, 'normal', 7, 0, 2, 12) exact_mean=18.233 sampled_mean=18.330 exact_support=133 sampled_support=66
- (4, 'elven_accuracy', 13, 1, 6, 24) exact_mean=28.328 sampled_mean=28.041 exact_support=476 sampled_support=98

### numpy 4,000

- (1, 'normal', 7, 0, 2, 12) exact_mean=11.688 sampled_mean=11.748 exact_support=87 sampled_support=51
- (3, 'normal', 7, 0, 2, 12) exact_mean=18.233 sampled_mean=18.247 exact_support=133 sampled_support=69
- (4, 'elven_accuracy', 13, 1, 6, 24) exact_mean=28.328 sampled_mean=28.232 exact_support=476 sampled_support=96

### numpy 32,000

- (1, 'normal', 7, 0, 2, 12) exact_mean=11.688 sampled_mean=11.627 exact_support=87 sampled_support=56
- (3, 'normal', 7, 0, 2, 12) exact_mean=18.233 sampled_mean=18.154 exact_support=133 sampled_support=81
- (4, 'elven_accuracy', 13, 1, 6, 24) exact_mean=28.328 sampled_mean=28.342 exact_support=476 sampled_support=131
