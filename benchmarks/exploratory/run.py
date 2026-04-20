#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile
from time import perf_counter


if __package__ in (None, ""):
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from benchmarks import common
    from benchmarks.fast.cases import PreparedEvalInstance
    from benchmarks.exploratory.cases import CASE
else:
    from benchmarks import common
    from benchmarks.fast.cases import PreparedEvalInstance
    from benchmarks.exploratory.cases import CASE


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        choices=common.OUTPUT_MODES,
        default="local",
        help="Write benchmark artifacts to benchmarks/results/<mode>/.",
    )
    parser.add_argument(
        "--max-cells",
        type=int,
        default=30000,
        help="Target maximum realized sweep-cell count for the exploratory plot.",
    )
    parser.add_argument(
        "--points",
        type=int,
        default=10,
        help="Number of linearly spaced sweep-cell targets to sample.",
    )
    parser.add_argument(
        "--plot-path",
        default=None,
        help="Optional PNG output path. Defaults to benchmarks/results/<mode>/exploratory_chaos_bolt_scaling.png.",
    )
    return parser.parse_args()


def linearly_spaced_targets(max_cells: int, points: int) -> tuple[int, ...]:
    if points <= 0:
        raise ValueError("points must be positive")
    return tuple(round(max_cells * index / points) for index in range(1, points + 1))


def selected_scales(max_cells: int, points: int) -> tuple[int, ...]:
    targets = linearly_spaced_targets(max_cells, points)
    sorted_points = sorted(CASE.points, key=lambda point: (point.cells, point.step))
    chosen_steps = []
    used_steps = set()
    scan_index = 0
    for target in targets:
        while scan_index < len(sorted_points) and sorted_points[scan_index].cells < target:
            scan_index += 1
        candidate_index = scan_index
        while candidate_index < len(sorted_points) and sorted_points[candidate_index].step in used_steps:
            candidate_index += 1
        if candidate_index >= len(sorted_points):
            break
        chosen_steps.append(sorted_points[candidate_index].step)
        used_steps.add(sorted_points[candidate_index].step)
    return tuple(chosen_steps)


def measure_scale(scale: int):
    point = CASE.point(scale)
    instance = PreparedEvalInstance(
        setup_program=point.setup_program,
        expression=point.expression,
        source_name=f"<benchmark:exploratory:{CASE.benchmark_id}:{point.step}>",
    )
    instance.reset()
    start = perf_counter()
    instance.run_once()
    elapsed = perf_counter() - start
    return {
        "scale": scale,
        "cells": point.cells,
        "label": point.label,
        "summary": common.summarize_samples([elapsed]),
        "samples_s": [elapsed],
    }


def default_plot_path(output_mode: str) -> Path:
    base_dir = common.RESULTS_DIR / output_mode
    return base_dir / "exploratory_chaos_bolt_scaling.png"


def plot_results(rows, plot_path: Path, max_cells: int) -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    mpl_config = Path(tempfile.gettempdir()) / "dice-mplconfig"
    mpl_config.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))

    import matplotlib.pyplot as plt

    # The hypercube traversal does not grow cell count monotonically, so sort by
    # realized cell count for this exploratory scaling view.
    plot_rows = sorted(rows, key=lambda row: (row["cells"], row["scale"]))
    xs = [row["cells"] for row in plot_rows]
    ys = [row["summary"]["median"] for row in plot_rows]

    figure, axis = plt.subplots(1, 1, figsize=(11, 6))
    axis.plot(xs, ys, color="#1f77b4", marker="o", linewidth=1.8, markersize=5)
    axis.set_title("Chaos Bolt Exact Scaling")
    axis.set_xlabel("Sweep cells")
    axis.set_ylabel("Elapsed time (s)")
    axis.set_xscale("linear")
    axis.set_yscale("linear")
    axis.set_xlim(0, max_cells)
    axis.grid(True, alpha=0.25)

    figure.tight_layout()
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(plot_path, dpi=170, bbox_inches="tight")
    plt.close(figure)


def render_markdown(payload, plot_path: Path | None):
    lines = [
        "# {}".format(payload["benchmark_name"]),
        "",
        "## Run Metadata",
        "",
        "- timestamp: {}".format(payload["environment"]["timestamp"]),
        "- git commit: {}".format(payload["environment"]["git_commit"]),
        "- git branch: {}".format(payload["environment"]["git_branch"]),
        "- worktree dirty: {}".format("yes" if payload["environment"]["git_dirty"] else "no"),
        "- host: {}".format(payload["environment"]["hostname"]),
        "- platform: {}".format(payload["environment"]["platform"]),
        "- python: {}".format(payload["environment"]["python_version"]),
        "",
        "## Configuration",
        "",
        "- case: {}".format(payload["config"]["case"]),
        "- max cells: {}".format(payload["config"]["max_cells"]),
        "- points: {}".format(payload["config"]["points"]),
        "- sampling: first frontier point at or above each linearly spaced cell target",
        "- axes: linear / linear",
        "- x axis: realized sweep cells (sorted for plotting)",
        "",
    ]
    if plot_path is not None:
        lines.extend(
            [
                "## Plot",
                "",
                "![Chaos Bolt exploratory scaling]({})".format(plot_path),
                "",
            ]
        )

    lines.extend(
        [
            "## Samples",
            "",
            common.markdown_table(
                ("Step", "Cells", "Elapsed (s)", "Stdev (s)", "StdErr Mean (s)", "Label"),
                [
                    (
                        row["scale"],
                        row["cells"],
                        "{:.3f}".format(row["summary"]["median"]),
                        "{:.3f}".format(row["summary"]["stdev"]),
                        "{:.3f}".format(row["summary"]["stderr_mean"]),
                        row["label"],
                    )
                    for row in payload["rows"]
                ],
            ),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main():
    args = parse_args()
    scales = selected_scales(args.max_cells, args.points)
    rows = []

    print("Exploratory benchmark: Chaos Bolt exact scaling")
    print("frontier traversal: hypercube shells from benchmarks/slow/cases.py")
    print("sampling strategy: {} linearly spaced sweep-cell targets".format(args.points))
    print("max cells: {}".format(args.max_cells))
    print()

    for scale in scales:
        row = measure_scale(scale)
        rows.append(row)
        print(
            "step {:>3} | cells {:>4} | time {:>7.3f}s | {}".format(
                row["scale"],
                row["cells"],
                row["summary"]["median"],
                row["label"],
            )
        )

    plot_path = None
    if args.output != "none" or args.plot_path is not None:
        plot_path = Path(args.plot_path) if args.plot_path else default_plot_path(args.output)
        plot_results(rows, plot_path, args.max_cells)

    payload = {
        "schema_version": 1,
        "benchmark_id": "exploratory_chaos_bolt_scaling",
        "benchmark_name": "Exploratory: Chaos Bolt Exact Scaling",
        "category": "exploratory",
        "environment": common.benchmark_environment(),
        "config": {
            "case": CASE.benchmark_id,
            "max_cells": args.max_cells,
            "points": args.points,
        },
        "rows": rows,
    }

    artifact_paths = common.write_artifact_bundle(
        payload["benchmark_id"],
        args.output,
        payload,
        render_markdown(payload, plot_path),
    )
    if plot_path is not None:
        print()
        print("Plot written to {}".format(plot_path))
    if artifact_paths is not None:
        print("Artifacts written to {} and {}".format(*artifact_paths))


if __name__ == "__main__":
    main()
