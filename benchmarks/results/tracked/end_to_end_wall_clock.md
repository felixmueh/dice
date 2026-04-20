# End-to-End Benchmarks

## Run Metadata

- timestamp: 2026-04-20T22:27:08+02:00
- git commit: None
- git branch: None
- run context: during-commit
- worktree dirty: no
- host: fedora.fritz.box
- platform: Linux-6.19.11-200.fc43.x86_64-x86_64-with-glibc2.42
- python: 3.14.3

## Configuration

- timed rounds: 9
- warmup rounds: 2
- parsing included: yes
- interpreter startup included: yes
- session reuse: no

## Results

| Benchmark                     | Median (ms) | Mean (ms) | Min (ms) | Max (ms) | Stdev (ms) | StdErr Mean (ms) | Rounds |
| ----------------------------- | ----------- | --------- | -------- | -------- | ---------- | ---------------- | ------ |
| Scalar Addition Program       | 0.340       | 0.344     | 0.327    | 0.387    | 0.019      | 0.006            | 9      |
| Distribution Addition Program | 0.369       | 0.381     | 0.358    | 0.451    | 0.029      | 0.010            | 9      |
| DSL Function Program          | 0.631       | 0.641     | 0.625    | 0.693    | 0.021      | 0.007            | 9      |
| Attack Sweep Program          | 1.013       | 1.165     | 0.988    | 2.377    | 0.455      | 0.152            | 9      |
| Stdlib Import Program         | 14.899      | 15.084    | 14.444   | 16.745   | 0.734      | 0.245            | 9      |

## Comparison Against Previous Tracked Result

| Benchmark                     | Current (ms) | Tracked (ms) | Delta (ms) | Delta (%) | Threshold (ms) | Status |
| ----------------------------- | ------------ | ------------ | ---------- | --------- | -------------- | ------ |
| Scalar Addition Program       | 0.340        | 0.324        | +0.015     | +4.7%     | 0.032          | stable |
| Distribution Addition Program | 0.369        | 0.350        | +0.019     | +5.5%     | 0.035          | stable |
| DSL Function Program          | 0.631        | 0.650        | -0.019     | -2.9%     | 0.065          | stable |
| Attack Sweep Program          | 1.013        | 1.053        | -0.040     | -3.8%     | 0.339          | stable |
| Stdlib Import Program         | 14.899       | 16.199       | -1.300     | -8.0%     | 1.620          | stable |
