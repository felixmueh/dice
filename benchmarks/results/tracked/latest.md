# Benchmark Report (tracked)

## End-to-End Benchmarks

Run: commit `None` on `fedora.fritz.box` at 2026-04-20T21:51:09+02:00 [during-commit]

| Benchmark                     | Median (ms) | Mean (ms) | Stdev (ms) | StdErr Mean (ms) |
| ----------------------------- | ----------- | --------- | ---------- | ---------------- |
| Scalar Addition Program       | 0.354       | 0.392     | 0.106      | 0.035            |
| Distribution Addition Program | 0.361       | 0.370     | 0.030      | 0.010            |
| DSL Function Program          | 0.617       | 0.620     | 0.015      | 0.005            |
| Attack Sweep Program          | 1.029       | 1.412     | 1.163      | 0.388            |
| Stdlib Import Program         | 14.775      | 14.963    | 0.932      | 0.311            |

## Fast Benchmarks: Prepared Evaluation

Run: commit `None` on `fedora.fritz.box` at 2026-04-20T21:51:09+02:00 [during-commit]

| Benchmark                  | Mode | Median (ms) | Mean (ms) | Stdev (ms) | StdErr Mean (ms) |
| -------------------------- | ---- | ----------- | --------- | ---------- | ---------------- |
| Scalar Addition            | cold | 0.020       | 0.023     | 0.008      | 0.003            |
| Scalar Addition            | warm | 0.007       | 0.007     | 0.001      | 0.000            |
| Distribution Addition      | cold | 0.067       | 0.073     | 0.012      | 0.004            |
| Distribution Addition      | warm | 0.013       | 0.014     | 0.003      | 0.001            |
| Binary Roll                | cold | 0.067       | 0.079     | 0.032      | 0.011            |
| Binary Roll                | warm | 0.006       | 0.009     | 0.007      | 0.002            |
| Keep High                  | cold | 0.490       | 0.560     | 0.115      | 0.038            |
| Keep High                  | warm | 0.009       | 0.013     | 0.007      | 0.002            |
| Threshold Compare          | cold | 0.032       | 0.040     | 0.013      | 0.004            |
| Threshold Compare          | warm | 0.010       | 0.015     | 0.016      | 0.005            |
| Branching Damage           | cold | 0.044       | 0.050     | 0.012      | 0.004            |
| Branching Damage           | warm | 0.016       | 0.017     | 0.003      | 0.001            |
| Mean Summary               | cold | 0.052       | 0.059     | 0.014      | 0.005            |
| Mean Summary               | warm | 0.023       | 0.024     | 0.005      | 0.002            |
| Cumulative Distribution    | cold | 0.044       | 0.046     | 0.008      | 0.003            |
| Cumulative Distribution    | warm | 0.010       | 0.011     | 0.002      | 0.001            |
| Survival Distribution      | cold | 0.041       | 0.042     | 0.006      | 0.002            |
| Survival Distribution      | warm | 0.010       | 0.010     | 0.002      | 0.001            |
| Repeat Sum                 | cold | 0.120       | 0.132     | 0.025      | 0.008            |
| Repeat Sum                 | warm | 0.012       | 0.013     | 0.003      | 0.001            |
| Pure DSL Scalar Call       | cold | 0.024       | 0.026     | 0.007      | 0.002            |
| Pure DSL Scalar Call       | warm | 0.006       | 0.006     | 0.002      | 0.001            |
| Pure DSL Distribution Call | cold | 0.077       | 0.092     | 0.037      | 0.012            |
| Pure DSL Distribution Call | warm | 0.011       | 0.013     | 0.005      | 0.002            |
| Attack vs AC Sweep         | cold | 0.324       | 0.351     | 0.081      | 0.027            |
| Attack vs AC Sweep         | warm | 0.113       | 0.127     | 0.030      | 0.010            |
| Damage vs AC Sweep         | cold | 1.845       | 1.843     | 0.083      | 0.028            |
| Damage vs AC Sweep         | warm | 0.232       | 0.238     | 0.016      | 0.005            |
| Two-Axis Damage Sweep      | cold | 3.362       | 3.417     | 0.132      | 0.044            |
| Two-Axis Damage Sweep      | warm | 0.476       | 0.509     | 0.091      | 0.030            |

## Monte Carlo Comparison: Chaos Bolt chain (comparison)

Run: commit `None` on `fedora.fritz.box` at 2026-04-20T21:52:49+02:00 [during-commit]

| Backend                      | Samples / cell | Scope                    | Time (s) | Stdev (s) | StdErr Mean (s) | vs dice | Rep. mean abs err |
| ---------------------------- | -------------- | ------------------------ | -------- | --------- | --------------- | ------- | ----------------- |
| dice exact (naive DSL)       | -              | full sweep (1,536 cells) | 23.957   | 0.000     | 0.000           | 1.00x   | 0.0000            |
| dice exact (delta DSL)       | -              | full sweep (1,536 cells) | 21.128   | 0.000     | 0.000           | 0.88x   | 0.0000            |
| dice exact (host functions)  | -              | full sweep (1,536 cells) | 1.233    | 0.000     | 0.000           | 0.05x   | 0.0000            |
| Naive Python Monte Carlo     | 4,000          | full sweep (1,536 cells) | 10.529   | 0.000     | 0.000           | 0.44x   | 0.1711            |
| Vectorized NumPy Monte Carlo | 4,000          | full sweep (1,536 cells) | 0.488    | 0.000     | 0.000           | 0.02x   | 0.0574            |
| Vectorized NumPy Monte Carlo | 32,000         | full sweep (1,536 cells) | 0.776    | 0.000     | 0.000           | 0.03x   | 0.0506            |

## Monte Carlo Comparison: Hexed/Blessed Scorching Ray

Run: commit `None` on `fedora.fritz.box` at 2026-04-20T21:51:51+02:00 [during-commit]

| Backend                      | Samples / cell | Scope                    | Time (s) | Stdev (s) | StdErr Mean (s) | vs dice | Rep. mean abs err |
| ---------------------------- | -------------- | ------------------------ | -------- | --------- | --------------- | ------- | ----------------- |
| dice exact                   | -              | full sweep (1,260 cells) | 0.522    | 0.000     | 0.000           | 1.00x   | 0.0000            |
| Naive Python Monte Carlo     | 4,000          | full sweep (1,260 cells) | 33.547   | 0.000     | 0.000           | 64.30x  | 0.2184            |
| Vectorized NumPy Monte Carlo | 4,000          | full sweep (1,260 cells) | 0.384    | 0.000     | 0.000           | 0.74x   | 0.2923            |
| Vectorized NumPy Monte Carlo | 32,000         | full sweep (1,260 cells) | 0.700    | 0.000     | 0.000           | 1.34x   | 0.0861            |

## Slow Benchmarks: Budget Frontier

Run: commit `None` on `fedora.fritz.box` at 2026-04-20T21:51:15+02:00 [during-commit]

| Benchmark                    | Budget (s) | Max Scale | Unit  | Frontier Median (s) | Stdev (s) | StdErr Mean (s) |
| ---------------------------- | ---------- | --------- | ----- | ------------------- | --------- | --------------- |
| Damage Sweep Frontier        | 1.00       | 42        | cells | 0.022               | 0.000     | 0.000           |
| Hexed Scorching Ray Frontier | 1.00       | 360       | cells | 0.713               | 0.000     | 0.000           |
| Chaos Bolt Chain Frontier    | 1.00       | 61        | cells | 0.645               | 0.000     | 0.000           |
