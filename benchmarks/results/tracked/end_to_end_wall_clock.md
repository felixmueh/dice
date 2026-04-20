# End-to-End Benchmarks

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
- parsing included: yes
- interpreter startup included: yes
- session reuse: no

## Results

| Benchmark                     | Median (ms) | Mean (ms) | Min (ms) | Max (ms) | Stdev (ms) | StdErr Mean (ms) | Rounds |
| ----------------------------- | ----------- | --------- | -------- | -------- | ---------- | ---------------- | ------ |
| Scalar Addition Program       | 0.354       | 0.392     | 0.313    | 0.650    | 0.106      | 0.035            | 9      |
| Distribution Addition Program | 0.361       | 0.370     | 0.340    | 0.438    | 0.030      | 0.010            | 9      |
| DSL Function Program          | 0.617       | 0.620     | 0.604    | 0.644    | 0.015      | 0.005            | 9      |
| Attack Sweep Program          | 1.029       | 1.412     | 0.897    | 4.497    | 1.163      | 0.388            | 9      |
| Stdlib Import Program         | 14.775      | 14.963    | 14.058   | 17.159   | 0.932      | 0.311            | 9      |
