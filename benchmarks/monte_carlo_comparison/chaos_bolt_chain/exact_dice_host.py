"""Host-function-backed exact dice backend for the Chaos Bolt chain workload."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dice import dice_interpreter

from .workload import AXIS_ORDER, DEFAULT_CONFIG, build_host_dice_program


PACKAGE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ExactSweepResult:
    sweep: object
    cells: dict[tuple[object, ...], object]


def evaluate_exact_sweep(config=DEFAULT_CONFIG):
    session = dice_interpreter(current_dir=str(PACKAGE_DIR))
    sweep = session(build_host_dice_program(config), current_dir=PACKAGE_DIR)
    axis_names = tuple(axis.name for axis in sweep.axes)
    index_by_name = {name: axis_names.index(name) for name in AXIS_ORDER}
    cells = {}
    for coordinates, distribution in sweep.items():
        normalized = tuple(coordinates[index_by_name[name]] for name in AXIS_ORDER)
        cells[normalized] = distribution
    return ExactSweepResult(sweep=sweep, cells=cells)
