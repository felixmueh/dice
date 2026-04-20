# Benchmark Report (tracked)

## End-to-End Benchmarks

Run: commit `None` on `fedora.fritz.box` at 2026-04-20T22:27:08+02:00 [during-commit]

| Benchmark                     | Median (ms) | Mean (ms) | Stdev (ms) | StdErr Mean (ms) |
| ----------------------------- | ----------- | --------- | ---------- | ---------------- |
| Scalar Addition Program       | 0.340       | 0.344     | 0.019      | 0.006            |
| Distribution Addition Program | 0.369       | 0.381     | 0.029      | 0.010            |
| DSL Function Program          | 0.631       | 0.641     | 0.021      | 0.007            |
| Attack Sweep Program          | 1.013       | 1.165     | 0.455      | 0.152            |
| Stdlib Import Program         | 14.899      | 15.084    | 0.734      | 0.245            |

Comparison Against Previous Tracked Result

| Benchmark                     | Current (ms) | Tracked (ms) | Delta (ms) | Delta (%) | Threshold (ms) | Status |
| ----------------------------- | ------------ | ------------ | ---------- | --------- | -------------- | ------ |
| Scalar Addition Program       | 0.340        | 0.324        | +0.015     | +4.7%     | 0.032          | stable |
| Distribution Addition Program | 0.369        | 0.350        | +0.019     | +5.5%     | 0.035          | stable |
| DSL Function Program          | 0.631        | 0.650        | -0.019     | -2.9%     | 0.065          | stable |
| Attack Sweep Program          | 1.013        | 1.053        | -0.040     | -3.8%     | 0.339          | stable |
| Stdlib Import Program         | 14.899       | 16.199       | -1.300     | -8.0%     | 1.620          | stable |

## Fast Benchmarks: Prepared Evaluation

- 1 + 1: improvement vs tracked baseline (-13.5% / -0.003 ms; threshold 0.002 ms)
- 17 - 9: improvement vs tracked baseline (-11.0% / -0.002 ms; threshold 0.001 ms)
- 6 * 7: improvement vs tracked baseline (-12.2% / -0.002 ms; threshold 0.001 ms)
- 21 / 3: improvement vs tracked baseline (-13.9% / -0.002 ms; threshold 0.001 ms)
- 21 // 4: improvement vs tracked baseline (-11.7% / -0.002 ms; threshold 0.001 ms)
- ([PLAN:1, 2] + [AC:10, 11])["AC", "PLAN"]: improvement vs tracked baseline (-10.1% / -0.008 ms; threshold 0.008 ms)

Run: commit `None` on `fedora.fritz.box` at 2026-04-20T22:27:08+02:00 [during-commit]

| Benchmark                                                                               | Mode | Median (ms) | Mean (ms) | Stdev (ms) | StdErr Mean (ms) |
| --------------------------------------------------------------------------------------- | ---- | ----------- | --------- | ---------- | ---------------- |
| 1 + 1                                                                                   | -    | 0.018       | 0.019     | 0.005      | 0.000            |
| 17 - 9                                                                                  | -    | 0.013       | 0.014     | 0.002      | 0.000            |
| 6 * 7                                                                                   | -    | 0.012       | 0.012     | 0.001      | 0.000            |
| 21 / 3                                                                                  | -    | 0.013       | 0.013     | 0.002      | 0.000            |
| 21 // 4                                                                                 | -    | 0.011       | 0.012     | 0.002      | 0.000            |
| -(d6)                                                                                   | -    | 0.031       | 0.032     | 0.003      | 0.000            |
| d20 + d8                                                                                | -    | 0.068       | 0.069     | 0.006      | 0.000            |
| d20 >= d12                                                                              | -    | 0.140       | 0.148     | 0.081      | 0.006            |
| d20 in {1, 20}                                                                          | -    | 0.049       | 0.052     | 0.025      | 0.002            |
| 3 d 6                                                                                   | -    | 0.072       | 0.075     | 0.025      | 0.002            |
| 4 d 6 h 3                                                                               | -    | 0.537       | 0.555     | 0.144      | 0.010            |
| 4 d 6 l 3                                                                               | -    | 0.545       | 0.544     | 0.017      | 0.001            |
| d20 >= 11 -> 8 \| 0                                                                     | -    | 0.052       | 0.053     | 0.005      | 0.000            |
| mean(d20 >= 11 -> 8 \| 0)                                                               | -    | 0.056       | 0.058     | 0.005      | 0.000            |
| var(d20 + d8)                                                                           | -    | 0.085       | 0.086     | 0.010      | 0.001            |
| std(d20 + d8)                                                                           | -    | 0.080       | 0.081     | 0.006      | 0.000            |
| cum(d20)                                                                                | -    | 0.043       | 0.044     | 0.004      | 0.000            |
| surv(d20)                                                                               | -    | 0.041       | 0.041     | 0.003      | 0.000            |
| repeat_sum(8, d6)                                                                       | -    | 0.128       | 0.130     | 0.008      | 0.001            |
| [AC:10..25] + 7                                                                         | -    | 0.156       | 0.159     | 0.012      | 0.001            |
| d20 >= [AC:10..25]                                                                      | -    | 0.150       | 0.152     | 0.009      | 0.001            |
| ([PLAN:1, 2] + [AC:10, 11])["AC", "PLAN"]                                               | -    | 0.073       | 0.075     | 0.006      | 0.000            |
| ([PLAN:1, 2] + [AC:10, 11])[PLAN: 2]                                                    | -    | 0.061       | 0.062     | 0.004      | 0.000            |
| ([PLAN:1, 2] + [AC:10, 11, 12])[AC in {10, 12}]                                         | -    | 0.089       | 0.090     | 0.004      | 0.000            |
| ([PLAN:1, 2] + [AC:10, 11])[1, 0]                                                       | -    | 0.064       | 0.064     | 0.002      | 0.000            |
| sumover([PLAN:1, 2] + [AC:10, 11], "PLAN")                                              | -    | 0.107       | 0.109     | 0.005      | 0.000            |
| meanover(d2 + [bonus:0, 1], "bonus")                                                    | -    | 0.058       | 0.059     | 0.004      | 0.000            |
| maxover([PLAN:1, 2] + [AC:10, 11], "PLAN")                                              | -    | 0.068       | 0.073     | 0.041      | 0.003            |
| argmaxover([PLAN:1, 2] + [AC:10, 11], "PLAN")                                           | -    | 0.071       | 0.075     | 0.034      | 0.002            |
| sumover([PLAN:1, 2] + [LEVEL:10, 20] + [AC:100, 200], ("PLAN", "LEVEL"))                | -    | 0.212       | 0.218     | 0.053      | 0.004            |
| meanover([PLAN:1, 2] + [LEVEL:10, 20], ("PLAN", "LEVEL"))                               | -    | 0.070       | 0.071     | 0.005      | 0.000            |
| repeat_sum(2, d20 >= [AC:10..25] -> 1 \| 0)                                             | -    | 0.482       | 0.486     | 0.017      | 0.001            |
| repeat_sum(4, d6 + (d20 + 7 >= [AC:10..28] -> 3 \| 0))                                  | -    | 1.937       | 1.961     | 0.080      | 0.006            |
| repeat_sum(4, d6 + (d20 + 7 + ([BLESS:0, 1] == 1 -> d4 \| 0) >= [AC:10..26] -> 3 \| 0)) | -    | 3.585       | 3.650     | 0.280      | 0.020            |

Comparison Against Previous Tracked Result

| Benchmark                                                                               | Mode | Current (ms) | Tracked (ms) | Delta (ms) | Delta (%) | Threshold (ms) | Status      |
| --------------------------------------------------------------------------------------- | ---- | ------------ | ------------ | ---------- | --------- | -------------- | ----------- |
| 1 + 1                                                                                   | -    | 0.018        | 0.020        | -0.003     | -13.5%    | 0.002          | improvement |
| 17 - 9                                                                                  | -    | 0.013        | 0.015        | -0.002     | -11.0%    | 0.001          | improvement |
| 6 * 7                                                                                   | -    | 0.012        | 0.013        | -0.002     | -12.2%    | 0.001          | improvement |
| 21 / 3                                                                                  | -    | 0.013        | 0.015        | -0.002     | -13.9%    | 0.001          | improvement |
| 21 // 4                                                                                 | -    | 0.011        | 0.013        | -0.002     | -11.7%    | 0.001          | improvement |
| -(d6)                                                                                   | -    | 0.031        | 0.033        | -0.003     | -7.9%     | 0.003          | stable      |
| d20 + d8                                                                                | -    | 0.068        | 0.069        | -0.001     | -1.8%     | 0.007          | stable      |
| d20 >= d12                                                                              | -    | 0.140        | 0.142        | -0.003     | -1.8%     | 0.014          | stable      |
| d20 in {1, 20}                                                                          | -    | 0.049        | 0.053        | -0.005     | -9.1%     | 0.005          | stable      |
| 3 d 6                                                                                   | -    | 0.072        | 0.075        | -0.003     | -3.6%     | 0.007          | stable      |
| 4 d 6 h 3                                                                               | -    | 0.537        | 0.538        | -0.001     | -0.2%     | 0.054          | stable      |
| 4 d 6 l 3                                                                               | -    | 0.545        | 0.543        | +0.002     | +0.4%     | 0.054          | stable      |
| d20 >= 11 -> 8 \| 0                                                                     | -    | 0.052        | 0.055        | -0.003     | -6.1%     | 0.005          | stable      |
| mean(d20 >= 11 -> 8 \| 0)                                                               | -    | 0.056        | 0.061        | -0.005     | -7.9%     | 0.006          | stable      |
| var(d20 + d8)                                                                           | -    | 0.085        | 0.089        | -0.005     | -5.2%     | 0.009          | stable      |
| std(d20 + d8)                                                                           | -    | 0.080        | 0.083        | -0.004     | -4.4%     | 0.008          | stable      |
| cum(d20)                                                                                | -    | 0.043        | 0.045        | -0.002     | -4.7%     | 0.005          | stable      |
| surv(d20)                                                                               | -    | 0.041        | 0.042        | -0.002     | -4.0%     | 0.004          | stable      |
| repeat_sum(8, d6)                                                                       | -    | 0.128        | 0.131        | -0.003     | -2.5%     | 0.013          | stable      |
| [AC:10..25] + 7                                                                         | -    | 0.156        | 0.168        | -0.011     | -6.7%     | 0.017          | stable      |
| d20 >= [AC:10..25]                                                                      | -    | 0.150        | 0.154        | -0.004     | -2.6%     | 0.015          | stable      |
| ([PLAN:1, 2] + [AC:10, 11])["AC", "PLAN"]                                               | -    | 0.073        | 0.081        | -0.008     | -10.1%    | 0.008          | improvement |
| ([PLAN:1, 2] + [AC:10, 11])[PLAN: 2]                                                    | -    | 0.061        | 0.064        | -0.003     | -4.3%     | 0.006          | stable      |
| ([PLAN:1, 2] + [AC:10, 11, 12])[AC in {10, 12}]                                         | -    | 0.089        | 0.094        | -0.005     | -4.8%     | 0.009          | stable      |
| ([PLAN:1, 2] + [AC:10, 11])[1, 0]                                                       | -    | 0.064        | 0.067        | -0.003     | -4.6%     | 0.007          | stable      |
| sumover([PLAN:1, 2] + [AC:10, 11], "PLAN")                                              | -    | 0.107        | 0.113        | -0.005     | -4.8%     | 0.011          | stable      |
| meanover(d2 + [bonus:0, 1], "bonus")                                                    | -    | 0.058        | 0.061        | -0.003     | -5.0%     | 0.006          | stable      |
| maxover([PLAN:1, 2] + [AC:10, 11], "PLAN")                                              | -    | 0.068        | 0.072        | -0.004     | -5.7%     | 0.007          | stable      |
| argmaxover([PLAN:1, 2] + [AC:10, 11], "PLAN")                                           | -    | 0.071        | 0.077        | -0.006     | -7.7%     | 0.008          | stable      |
| sumover([PLAN:1, 2] + [LEVEL:10, 20] + [AC:100, 200], ("PLAN", "LEVEL"))                | -    | 0.212        | 0.218        | -0.006     | -2.9%     | 0.022          | stable      |
| meanover([PLAN:1, 2] + [LEVEL:10, 20], ("PLAN", "LEVEL"))                               | -    | 0.070        | 0.073        | -0.003     | -3.5%     | 0.007          | stable      |
| repeat_sum(2, d20 >= [AC:10..25] -> 1 \| 0)                                             | -    | 0.482        | 0.493        | -0.011     | -2.1%     | 0.049          | stable      |
| repeat_sum(4, d6 + (d20 + 7 >= [AC:10..28] -> 3 \| 0))                                  | -    | 1.937        | 1.998        | -0.060     | -3.0%     | 0.200          | stable      |
| repeat_sum(4, d6 + (d20 + 7 + ([BLESS:0, 1] == 1 -> d4 \| 0) >= [AC:10..26] -> 3 \| 0)) | -    | 3.585        | 3.702        | -0.117     | -3.2%     | 0.370          | stable      |

## Monte Carlo Comparison: Chaos Bolt chain (comparison)

- Preset: comparison
- Axis order: SLOT, MODE, ATTACK, BLESS, TARGETS, AC
- Timing scope: full exact sweep across 1,536 cells
- Sample counts: baseline=4,000 numpy=4,000, 32,000
- NumPy config: processes=16 batch_size=50,000

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

- Axis order: SLOT, MODE, ATTACK, BLESS, AC
- Timing scope: full exact sweep across 1,260 cells
- Sample counts: baseline=4,000 numpy=4,000, 32,000
- NumPy config: processes=16 batch_size=50,000

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
