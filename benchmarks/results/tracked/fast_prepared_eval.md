# Fast Benchmarks: Prepared Evaluation

## Run Metadata

- timestamp: 2026-04-20T21:51:09+02:00
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
- interleaved execution: yes
- parsing included: no
- interpreter startup included: no

## Results

| Benchmark                  | Mode | Median (ms) | Mean (ms) | Min (ms) | Max (ms) | Stdev (ms) | StdErr Mean (ms) | Rounds |
| -------------------------- | ---- | ----------- | --------- | -------- | -------- | ---------- | ---------------- | ------ |
| Scalar Addition            | cold | 0.020       | 0.023     | 0.017    | 0.037    | 0.008      | 0.003            | 9      |
| Scalar Addition            | warm | 0.007       | 0.007     | 0.006    | 0.009    | 0.001      | 0.000            | 9      |
| Distribution Addition      | cold | 0.067       | 0.073     | 0.065    | 0.101    | 0.012      | 0.004            | 9      |
| Distribution Addition      | warm | 0.013       | 0.014     | 0.012    | 0.020    | 0.003      | 0.001            | 9      |
| Binary Roll                | cold | 0.067       | 0.079     | 0.065    | 0.163    | 0.032      | 0.011            | 9      |
| Binary Roll                | warm | 0.006       | 0.009     | 0.005    | 0.027    | 0.007      | 0.002            | 9      |
| Keep High                  | cold | 0.490       | 0.560     | 0.470    | 0.790    | 0.115      | 0.038            | 9      |
| Keep High                  | warm | 0.009       | 0.013     | 0.008    | 0.029    | 0.007      | 0.002            | 9      |
| Threshold Compare          | cold | 0.032       | 0.040     | 0.031    | 0.064    | 0.013      | 0.004            | 9      |
| Threshold Compare          | warm | 0.010       | 0.015     | 0.008    | 0.058    | 0.016      | 0.005            | 9      |
| Branching Damage           | cold | 0.044       | 0.050     | 0.042    | 0.074    | 0.012      | 0.004            | 9      |
| Branching Damage           | warm | 0.016       | 0.017     | 0.014    | 0.025    | 0.003      | 0.001            | 9      |
| Mean Summary               | cold | 0.052       | 0.059     | 0.049    | 0.091    | 0.014      | 0.005            | 9      |
| Mean Summary               | warm | 0.023       | 0.024     | 0.020    | 0.036    | 0.005      | 0.002            | 9      |
| Cumulative Distribution    | cold | 0.044       | 0.046     | 0.040    | 0.064    | 0.008      | 0.003            | 9      |
| Cumulative Distribution    | warm | 0.010       | 0.011     | 0.009    | 0.016    | 0.002      | 0.001            | 9      |
| Survival Distribution      | cold | 0.041       | 0.042     | 0.037    | 0.057    | 0.006      | 0.002            | 9      |
| Survival Distribution      | warm | 0.010       | 0.010     | 0.008    | 0.016    | 0.002      | 0.001            | 9      |
| Repeat Sum                 | cold | 0.120       | 0.132     | 0.117    | 0.195    | 0.025      | 0.008            | 9      |
| Repeat Sum                 | warm | 0.012       | 0.013     | 0.010    | 0.021    | 0.003      | 0.001            | 9      |
| Pure DSL Scalar Call       | cold | 0.024       | 0.026     | 0.021    | 0.042    | 0.007      | 0.002            | 9      |
| Pure DSL Scalar Call       | warm | 0.006       | 0.006     | 0.005    | 0.011    | 0.002      | 0.001            | 9      |
| Pure DSL Distribution Call | cold | 0.077       | 0.092     | 0.072    | 0.185    | 0.037      | 0.012            | 9      |
| Pure DSL Distribution Call | warm | 0.011       | 0.013     | 0.009    | 0.024    | 0.005      | 0.002            | 9      |
| Attack vs AC Sweep         | cold | 0.324       | 0.351     | 0.291    | 0.494    | 0.081      | 0.027            | 9      |
| Attack vs AC Sweep         | warm | 0.113       | 0.127     | 0.102    | 0.180    | 0.030      | 0.010            | 9      |
| Damage vs AC Sweep         | cold | 1.845       | 1.843     | 1.737    | 1.955    | 0.083      | 0.028            | 9      |
| Damage vs AC Sweep         | warm | 0.232       | 0.238     | 0.217    | 0.265    | 0.016      | 0.005            | 9      |
| Two-Axis Damage Sweep      | cold | 3.362       | 3.417     | 3.295    | 3.650    | 0.132      | 0.044            | 9      |
| Two-Axis Damage Sweep      | warm | 0.476       | 0.509     | 0.455    | 0.738    | 0.091      | 0.030            | 9      |
