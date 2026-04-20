# Monte Carlo Comparison Benchmarks

These benchmarks compare exact dice evaluation against Monte Carlo
implementations for larger workloads.

They are intentionally exploratory:

- they are not part of the automated test or commit flow
- they write local-only artifacts under `benchmarks/results/local/`
- their reports should not be checked in

Current workloads:

- `hexed_scorching_ray/`
- `chaos_bolt_chain/`
  This runner now compares three exact implementations before the sampled
  backends:
  the naive dice-language benchmark, a reduced-state dice-language rewrite,
  and a host-function rewrite that highlights the effect of per-call host
  caching.
