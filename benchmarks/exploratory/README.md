# Exploratory Benchmarks

This suite is for one-off scaling experiments that are useful during
development but do not define the stable benchmark contract.

The current runner measures the exact Chaos Bolt frontier along an exponential
ladder of hypercube-grown sweep points and plots wall-clock time against the
realized cell count.

Use it when you want a quick visual answer to "how does this workload scale as
the sweep grows outward across dimensions?"
