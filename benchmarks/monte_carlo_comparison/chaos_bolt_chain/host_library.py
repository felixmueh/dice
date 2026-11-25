"""Pure host-function implementation for Chaos Bolt chains."""

from __future__ import annotations

from functools import lru_cache

from dice import dicefunction
from dice.diceengine import Distribution, _deterministic_numeric_value, add


def _deterministic(value: int) -> Distribution:
    return Distribution(((value, 1.0),))


def _weighted_distribution(parts) -> Distribution:
    merged = {}
    for weight, distribution in parts:
        if weight == 0:
            continue
        for outcome, probability in distribution.items():
            merged[outcome] = merged.get(outcome, 0.0) + weight * probability
    return Distribution(tuple(merged.items()))


@lru_cache(maxsize=None)
def _roll_sum(count: int, sides: int) -> Distribution:
    if count == 0:
        return _deterministic(0)
    distribution = _deterministic(0)
    single = Distribution(((_outcome, 1.0 / sides) for _outcome in range(1, sides + 1)))
    for _ in range(count):
        distribution = add(distribution, single)
    return distribution


@lru_cache(maxsize=None)
def _mode_roll_distribution(mode: str) -> tuple[tuple[int, float], ...]:
    if mode == "normal":
        return tuple((outcome, 1.0 / 20.0) for outcome in range(1, 21))
    roll_count = 2 if mode == "advantage" else 3
    counts = {}
    total = 20 ** roll_count
    values = [1] * roll_count

    def visit(index: int):
        if index == roll_count:
            maximum = max(values)
            counts[maximum] = counts.get(maximum, 0) + 1
            return
        for outcome in range(1, 21):
            values[index] = outcome
            visit(index + 1)

    visit(0)
    return tuple(sorted((outcome, count / total) for outcome, count in counts.items()))


@lru_cache(maxsize=None)
def _bless_distribution(bless: int) -> tuple[tuple[int, float], ...]:
    if bless:
        return tuple((outcome, 0.25) for outcome in range(1, 5))
    return ((0, 1.0),)


@lru_cache(maxsize=None)
def _event_masses(mode: str, bless: int, delta: int) -> tuple[float, float, float]:
    miss = 0.0
    hit = 0.0
    crit = 0.0
    for attack_roll, attack_probability in _mode_roll_distribution(mode):
        if attack_roll == 1:
            miss += attack_probability
            continue
        if attack_roll == 20:
            crit += attack_probability
            continue
        for hit_bonus, bonus_probability in _bless_distribution(bless):
            if attack_roll + hit_bonus >= delta:
                hit += attack_probability * bonus_probability
            else:
                miss += attack_probability * bonus_probability
    return miss, hit, crit


@lru_cache(maxsize=None)
def _pair_sum_distribution(doubles: bool) -> Distribution:
    counts = {}
    total = 0
    for die1 in range(1, 9):
        for die2 in range(1, 9):
            if (die1 == die2) != doubles:
                continue
            total += 1
            pair_sum = die1 + die2
            counts[pair_sum] = counts.get(pair_sum, 0) + 1
    return Distribution((outcome, count / total) for outcome, count in counts.items())


@lru_cache(maxsize=None)
def _base_damage_distribution(slot_level: int, doubles: bool) -> Distribution:
    return add(_pair_sum_distribution(doubles), _roll_sum(slot_level, 6))


@lru_cache(maxsize=None)
def _crit_extra_distribution(slot_level: int) -> Distribution:
    return add(_roll_sum(2, 8), _roll_sum(slot_level, 6))


@lru_cache(maxsize=None)
def _crit_damage_distribution(slot_level: int, doubles: bool) -> Distribution:
    return add(_base_damage_distribution(slot_level, doubles), _crit_extra_distribution(slot_level))


@lru_cache(maxsize=None)
def _chaos_chain_distribution(slot_level: int, mode: str, bless: int, delta: int, targets: int) -> Distribution:
    miss_mass, hit_mass, crit_mass = _event_masses(mode, bless, delta)
    if targets <= 0:
        return _deterministic(0)
    if targets == 1:
        return _weighted_distribution(
            (
                (miss_mass, _deterministic(0)),
                (hit_mass * (7.0 / 8.0), _base_damage_distribution(slot_level, False)),
                (hit_mass * (1.0 / 8.0), _base_damage_distribution(slot_level, True)),
                (crit_mass * (7.0 / 8.0), _crit_damage_distribution(slot_level, False)),
                (crit_mass * (1.0 / 8.0), _crit_damage_distribution(slot_level, True)),
            )
        )
    previous = _chaos_chain_distribution(slot_level, mode, bless, delta, targets - 1)
    return _weighted_distribution(
        (
            (miss_mass, _deterministic(0)),
            (hit_mass * (7.0 / 8.0), _base_damage_distribution(slot_level, False)),
            (hit_mass * (1.0 / 8.0), add(_base_damage_distribution(slot_level, True), previous)),
            (crit_mass * (7.0 / 8.0), _crit_damage_distribution(slot_level, False)),
            (crit_mass * (1.0 / 8.0), add(_crit_damage_distribution(slot_level, True), previous)),
        )
    )


@dicefunction(pure=True)
def chaos_chain_host(slot_level, mode, bless, delta, targets):
    return _chaos_chain_distribution(
        int(_deterministic_numeric_value(slot_level, "chaos_chain_host", allow_float=False)),
        str(mode),
        int(_deterministic_numeric_value(bless, "chaos_chain_host", allow_float=False)),
        int(_deterministic_numeric_value(delta, "chaos_chain_host", allow_float=False)),
        int(_deterministic_numeric_value(targets, "chaos_chain_host", allow_float=False)),
    )
