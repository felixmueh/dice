#!/usr/bin/env python3

import unittest

from benchmarks.monte_carlo_comparison.chaos_bolt_chain import exact_dice, exact_dice_better, exact_dice_host, workload


EXACT_TOLERANCE = 1e-12


class BenchmarkVariantTests(unittest.TestCase):
    def test_chaos_bolt_exact_variants_agree(self):
        config = workload.SweepConfig(
            slots=(1,),
            modes=("normal", "advantage"),
            attack_bonuses=(9,),
            bless_values=(0, 1),
            target_counts=(2, 5),
            acs=(12, 18),
            label="test",
        )

        naive = exact_dice.evaluate_exact_sweep(config)
        better = exact_dice_better.evaluate_exact_sweep(config)
        host = exact_dice_host.evaluate_exact_sweep(config)

        self.assertEqual(set(naive.cells), set(better.cells))
        self.assertEqual(set(naive.cells), set(host.cells))

        for coordinate, reference in naive.cells.items():
            reference_items = dict(reference.items())
            for candidate in (better.cells[coordinate], host.cells[coordinate]):
                candidate_items = dict(candidate.items())
                outcomes = set(reference_items) | set(candidate_items)
                for outcome in outcomes:
                    self.assertAlmostEqual(
                        reference_items.get(outcome, 0.0),
                        candidate_items.get(outcome, 0.0),
                        delta=EXACT_TOLERANCE,
                        msg="mismatch at {} outcome {}".format(coordinate, outcome),
                    )


if __name__ == "__main__":
    unittest.main()
