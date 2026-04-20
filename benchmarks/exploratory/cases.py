from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from benchmarks.slow.cases import ChaosFrontierCase, _prefix_tiers


@dataclass(frozen=True)
class ExploratoryChaosFrontierCase(ChaosFrontierCase):
    @cached_property
    def slot_tiers(self):
        return _prefix_tiers((1, 2, 3, 4, 5, 6, 7, 8), (1, 2, 4, 6, 8))

    @cached_property
    def attack_tiers(self):
        return _prefix_tiers((5, 7, 9, 11, 13, 15, 17, 19), (1, 2, 4, 6, 8))

    @cached_property
    def target_tiers(self):
        return _prefix_tiers((2, 3, 4, 5, 6, 7, 8, 9), (1, 2, 4, 6, 8))

    @cached_property
    def ac_tiers(self):
        return _prefix_tiers((10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32), (2, 4, 6, 8, 10, 12))


CASE = ExploratoryChaosFrontierCase(
    benchmark_id="chaos_bolt_chain_exploratory_frontier",
    name="Chaos Bolt Chain Exploratory Frontier",
    description="Larger branch-heavy exact sweep grown outward across all sweep dimensions.",
)
