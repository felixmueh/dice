from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class EndToEndCase:
    benchmark_id: str
    name: str
    program: str
    description: str = ""


CASES = (
    EndToEndCase(
        benchmark_id="scalar_add",
        name="Scalar Addition Program",
        program="1 + 1",
        description="Minimal parse + startup + scalar evaluation.",
    ),
    EndToEndCase(
        benchmark_id="distribution_add",
        name="Distribution Addition Program",
        program="d20 + d8",
        description="Unswept exact convolution from a fresh session.",
    ),
    EndToEndCase(
        benchmark_id="dsl_function_program",
        name="DSL Function Program",
        program="""
double(value): value + value
double(d20)
""".strip(),
        description="Function definition plus invocation in a fresh session.",
    ),
    EndToEndCase(
        benchmark_id="attack_sweep_program",
        name="Attack Sweep Program",
        program="""
attack_damage(ac):
    d20 + 7 >= ac -> 8 | 0

attack_damage([AC:10..20])
""".strip(),
        description="Fresh-session parse and evaluation of a swept DSL helper.",
    ),
    EndToEndCase(
        benchmark_id="stdlib_import_program",
        name="Stdlib Import Program",
        program="""
import "std:dnd/core.dice"
attack(15, 7, 2 d 6 + 1 d 6, 4)
""".strip(),
        description="Import resolution plus evaluation in a fresh session.",
    ),
)
