from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from itertools import product
from pathlib import Path
from textwrap import dedent

from benchmarks.fast.cases import PreparedEvalInstance


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class FrontierPoint:
    step: int
    label: str
    cells: int
    setup_program: str | None
    expression: str


def _prefix_tiers(values, sizes):
    return tuple(tuple(values[:size]) for size in sizes)


def _tiered_value_lists(values):
    return ", ".join(str(value) for value in values)


def _tiered_string_lists(values):
    return ", ".join('"{}"'.format(value) for value in values)


def _hypercube_shell_indices(lengths):
    all_indices = product(*(range(length) for length in lengths))
    return tuple(sorted(all_indices, key=lambda item: (max(item), sum(item), item)))


@dataclass(frozen=True)
class FrontierCase:
    benchmark_id: str
    name: str
    description: str
    unit: str = "cells"

    @cached_property
    def points(self) -> tuple[FrontierPoint, ...]:
        return self._build_points()

    @property
    def max_scale(self) -> int:
        return len(self.points)

    def build_instance(self, scale: int) -> PreparedEvalInstance:
        point = self.points[max(1, min(scale, self.max_scale)) - 1]
        return PreparedEvalInstance(
            setup_program=point.setup_program,
            expression=point.expression,
            source_name=f"<benchmark:{self.benchmark_id}:{point.step}>",
        )

    def point(self, scale: int) -> FrontierPoint:
        return self.points[max(1, min(scale, self.max_scale)) - 1]

    def _build_points(self) -> tuple[FrontierPoint, ...]:
        raise NotImplementedError


@dataclass(frozen=True)
class DamageSweepFrontierCase(FrontierCase):
    @cached_property
    def ac_tiers(self):
        return _prefix_tiers(tuple(range(10, 74)), (4, 8, 16, 24, 32, 48, 64))

    @cached_property
    def repeat_tiers(self):
        return _prefix_tiers((1, 2, 3, 4, 5, 6, 8, 10, 12, 16), (1, 2, 4, 6, 8, 10))

    def _build_points(self) -> tuple[FrontierPoint, ...]:
        setup_program = (
            """
damage(ac, repeats):
    repeat_sum(repeats, d6 + (d20 + 7 >= ac -> 3 | 0))
""".strip()
        )
        points = []
        for step, (ac_index, repeat_index) in enumerate(
            _hypercube_shell_indices((len(self.ac_tiers), len(self.repeat_tiers))),
            start=1,
        ):
            ac_values = self.ac_tiers[ac_index]
            repeat_values = self.repeat_tiers[repeat_index]
            expression = "damage([AC:{}], [COUNT:{}])".format(
                _tiered_value_lists(ac_values),
                _tiered_value_lists(repeat_values),
            )
            cells = len(ac_values) * len(repeat_values)
            label = "ac={} repeats={} cells={}".format(len(ac_values), len(repeat_values), cells)
            points.append(FrontierPoint(step=step, label=label, cells=cells, setup_program=setup_program, expression=expression))
        return tuple(points)


@dataclass(frozen=True)
class HexedFrontierCase(FrontierCase):
    @cached_property
    def slot_tiers(self):
        return _prefix_tiers(tuple(range(2, 9)), (1, 2, 4, 7))

    @cached_property
    def mode_tiers(self):
        return _prefix_tiers(("normal", "advantage", "elven_accuracy"), (1, 2, 3))

    @cached_property
    def attack_tiers(self):
        return _prefix_tiers((7, 9, 11), (1, 2, 3))

    @cached_property
    def bless_tiers(self):
        return _prefix_tiers((0, 1), (1, 2))

    @cached_property
    def ac_tiers(self):
        return _prefix_tiers(tuple(range(13, 29)), (2, 4, 8, 12, 16))

    def _build_points(self) -> tuple[FrontierPoint, ...]:
        setup_program = (
            """
import "std:dnd/core.dice"

ray_roll_normal(): d20
ray_roll_advantage(): d+20
ray_roll_elven_accuracy(): 3d20h1

ray_roll(mode):
    split mode as name
    | name == "normal" -> ray_roll_normal()
    | name == "advantage" -> ray_roll_advantage()
    | otherwise -> ray_roll_elven_accuracy()

hexed_scorching_ray(ac, attack_bonus, slot_level=2, mode="normal", bless=0):
    roll = ray_roll(mode)
    hit_bonus = bless == 1 -> d4 | 0
    ray = attack(ac, attack_bonus, 2 d 6 + 1 d 6, 4, roll=roll, hit_bonus=hit_bonus)
    ray ^ (slot_level + 1)
""".strip()
        )
        lengths = (
            len(self.slot_tiers),
            len(self.mode_tiers),
            len(self.attack_tiers),
            len(self.bless_tiers),
            len(self.ac_tiers),
        )
        points = []
        for step, (slot_index, mode_index, attack_index, bless_index, ac_index) in enumerate(
            _hypercube_shell_indices(lengths),
            start=1,
        ):
            slots = self.slot_tiers[slot_index]
            modes = self.mode_tiers[mode_index]
            attacks = self.attack_tiers[attack_index]
            blesses = self.bless_tiers[bless_index]
            acs = self.ac_tiers[ac_index]
            expression = (
                'hexed_scorching_ray([AC:{acs}], [ATTACK:{attacks}], slot_level=[SLOT:{slots}], '
                'mode=[MODE:{modes}], bless=[BLESS:{blesses}])'
            ).format(
                acs=_tiered_value_lists(acs),
                attacks=_tiered_value_lists(attacks),
                slots=_tiered_value_lists(slots),
                modes=_tiered_string_lists(modes),
                blesses=_tiered_value_lists(blesses),
            )
            cells = len(slots) * len(modes) * len(attacks) * len(blesses) * len(acs)
            label = "slots={} modes={} attacks={} bless={} ac={} cells={}".format(
                len(slots), len(modes), len(attacks), len(blesses), len(acs), cells
            )
            points.append(FrontierPoint(step=step, label=label, cells=cells, setup_program=setup_program, expression=expression))
        return tuple(points)


@dataclass(frozen=True)
class ChaosFrontierCase(FrontierCase):
    @cached_property
    def slot_tiers(self):
        return _prefix_tiers((1, 4, 7), (1, 2, 3))

    @cached_property
    def mode_tiers(self):
        return _prefix_tiers(("normal", "advantage", "elven_accuracy"), (1, 2, 3))

    @cached_property
    def attack_tiers(self):
        return _prefix_tiers((9, 13, 17), (1, 2, 3))

    @cached_property
    def bless_tiers(self):
        return _prefix_tiers((0, 1), (1, 2))

    @cached_property
    def target_tiers(self):
        return _prefix_tiers((2, 3, 5), (1, 2, 3))

    @cached_property
    def ac_tiers(self):
        return _prefix_tiers(tuple(range(10, 18)), (2, 4, 6, 8))

    def _build_points(self) -> tuple[FrontierPoint, ...]:
        setup_program = (
            """
import "std:dnd/core.dice"

chain_roll_normal(): d20
chain_roll_advantage(): d+20
chain_roll_elven_accuracy(): 3d20h1

chain_roll(): split mode as name | name == "normal" -> chain_roll_normal() | name == "advantage" -> chain_roll_advantage() | otherwise -> chain_roll_elven_accuracy()
chaos_hit_bonus(): split bless | == 1 -> d4 | otherwise -> 0
chaos_crit_bonus(crit): split crit | == 1 -> 2 d 8 + (d6 ^ slot_level) | otherwise -> 0
chaos_resolve_pair(die1, leap_damage, crit_bonus): split d8 as die2 | die1 == die2 -> die1 + die2 + (d6 ^ slot_level) + crit_bonus + leap_damage | otherwise -> die1 + die2 + (d6 ^ slot_level) + crit_bonus
chaos_resolve_damage(leap_damage, crit): chaos_resolve_pair(d8, leap_damage, chaos_crit_bonus(crit))
chaos_strike(leap_damage): split chain_roll() as attack_roll | attack_roll == 1 -> 0 | attack_roll == 20 -> chaos_resolve_damage(leap_damage, 1) | attack_roll + attack_bonus + chaos_hit_bonus() >= ac -> chaos_resolve_damage(leap_damage, 0) ||

chaos_chain_1(): chaos_strike(0)
chaos_chain_2(): chaos_strike(chaos_chain_1())
chaos_chain_3(): chaos_strike(chaos_chain_2())
chaos_chain_4(): chaos_strike(chaos_chain_3())
chaos_chain_5(): chaos_strike(chaos_chain_4())
chaos_chain(): split targets as count | count == 2 -> chaos_chain_2() | count == 3 -> chaos_chain_3() | otherwise -> chaos_chain_5()
""".strip()
        )
        lengths = (
            len(self.slot_tiers),
            len(self.mode_tiers),
            len(self.attack_tiers),
            len(self.bless_tiers),
            len(self.target_tiers),
            len(self.ac_tiers),
        )
        points = []
        for step, (slot_index, mode_index, attack_index, bless_index, target_index, ac_index) in enumerate(
            _hypercube_shell_indices(lengths),
            start=1,
        ):
            slots = self.slot_tiers[slot_index]
            modes = self.mode_tiers[mode_index]
            attacks = self.attack_tiers[attack_index]
            blesses = self.bless_tiers[bless_index]
            targets = self.target_tiers[target_index]
            acs = self.ac_tiers[ac_index]
            expression = (
                dedent(
                    """
                    slot_level = [SLOT:{slots}]
                    mode = [MODE:{modes}]
                    attack_bonus = [ATTACK:{attacks}]
                    bless = [BLESS:{blesses}]
                    targets = [TARGETS:{targets}]
                    ac = [AC:{acs}]

                    chaos_chain()
                    """
                ).format(
                    slots=_tiered_value_lists(slots),
                    modes=_tiered_string_lists(modes),
                    attacks=_tiered_value_lists(attacks),
                    blesses=_tiered_value_lists(blesses),
                    targets=_tiered_value_lists(targets),
                    acs=_tiered_value_lists(acs),
                ).strip()
            )
            cells = len(slots) * len(modes) * len(attacks) * len(blesses) * len(targets) * len(acs)
            label = "slots={} modes={} attacks={} bless={} targets={} ac={} cells={}".format(
                len(slots), len(modes), len(attacks), len(blesses), len(targets), len(acs), cells
            )
            points.append(FrontierPoint(step=step, label=label, cells=cells, setup_program=setup_program, expression=expression))
        return tuple(points)


CASES = (
    DamageSweepFrontierCase(
        benchmark_id="damage_vs_ac_frontier",
        name="Damage Sweep Frontier",
        description="Prepared exact sweep over AC and repeat-count dimensions.",
    ),
    HexedFrontierCase(
        benchmark_id="hexed_scorching_ray_frontier",
        name="Hexed Scorching Ray Frontier",
        description="Large exact combat sweep grown outward across all sweep dimensions.",
    ),
    ChaosFrontierCase(
        benchmark_id="chaos_bolt_chain_frontier",
        name="Chaos Bolt Chain Frontier",
        description="Branch-heavy exact sweep grown outward across all sweep dimensions.",
    ),
)
