#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from time import perf_counter


if __package__ in (None, ""):
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from benchmarks import common
    from benchmarks.fast.cases import CASES
else:
    from benchmarks import common
    from benchmarks.fast.cases import CASES


@dataclass
class PreparedRun:
    case: object
    instance: object
    samples: list[float]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        choices=common.OUTPUT_MODES,
        default="local",
        help="Write benchmark artifacts to benchmarks/results/<mode>/.",
    )
    parser.add_argument("--rounds", type=int, default=200, help="Timed rounds per benchmark.")
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        help="Substring filter for benchmark ids. May be passed multiple times.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run fewer rounds for a smoke test.",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit non-zero if a tracked-baseline regression exceeds the configured threshold.",
    )
    return parser.parse_args()


def selected_cases(filters):
    if not filters:
        return CASES
    normalized = tuple(filter_value.lower() for filter_value in filters)
    return tuple(
        case
        for case in CASES
        if any(filter_value in case.benchmark_id.lower() for filter_value in normalized)
    )


def _benchmark_runs(cases):
    runs = []
    for case in cases:
        instance = case.build()
        runs.append(PreparedRun(case=case, instance=instance, samples=[]))
    return runs


def _time_once(run: PreparedRun) -> float:
    run.instance.reset()
    start = perf_counter()
    run.instance.run_once()
    return perf_counter() - start


def _run_interleaved(runs, rounds: int):
    for _ in range(rounds):
        for run in runs:
            run.samples.append(_time_once(run))


def render_markdown(payload, baseline_payload=None):
    lines = [
        "# {}".format(payload["benchmark_name"]),
        "",
    ]
    rendered_highlights = common.highlight_lines(payload)
    if rendered_highlights:
        lines.extend(["## Highlights", ""])
        for line in rendered_highlights:
            lines.append("- {}".format(line))
        lines.append("")
    lines.extend(
        [
            "## Run Metadata",
            "",
            "- timestamp: {}".format(payload["environment"]["timestamp"]),
            "- git commit: {}".format(payload["environment"]["git_commit"]),
            "- git branch: {}".format(payload["environment"]["git_branch"]),
            "- run context: {}".format(payload["environment"].get("run_context", "normal")),
            "- worktree dirty: {}".format("yes" if payload["environment"]["git_dirty"] else "no"),
            "- host: {}".format(payload["environment"]["hostname"]),
            "- platform: {}".format(payload["environment"]["platform"]),
            "- python: {}".format(payload["environment"]["python_version"]),
            "",
            "## Configuration",
            "",
            "- timed rounds: {}".format(payload["config"]["rounds"]),
            "- interleaved execution: yes",
            "- parsing included: no",
            "- interpreter startup included: no",
            "- cache reuse mode: no",
            "",
            "## Results",
            "",
            common.markdown_table(
            (
                "Construct",
                "Median (ms)",
                "Mean (ms)",
                "Min (ms)",
                "Max (ms)",
                "Stdev (ms)",
                "StdErr Mean (ms)",
                "Rounds",
            ),
            [
                (
                    row["construct"],
                    "{:.3f}".format(row["summary"]["median"] * 1000),
                    "{:.3f}".format(row["summary"]["mean"] * 1000),
                    "{:.3f}".format(row["summary"]["min"] * 1000),
                    "{:.3f}".format(row["summary"]["max"] * 1000),
                    "{:.3f}".format(row["summary"]["stdev"] * 1000),
                    "{:.3f}".format(row["summary"]["stderr_mean"] * 1000),
                    row["summary"]["count"],
                )
                for row in payload["rows"]
            ],
        ),
            "",
        ]
    )

    comparison_rows = common.comparison_rows(payload)
    if comparison_rows:
        lines.extend(
            [
                "## Comparison Against Previous Tracked Result",
                "",
                common.markdown_table(
                    ("Construct", "Current (ms)", "Tracked (ms)", "Delta (ms)", "Delta (%)", "Threshold (ms)", "Status"),
                    [
                        (
                            row["construct"],
                            "{:.3f}".format(row["current_median_s"] * 1000),
                            "{:.3f}".format(row["baseline_median_s"] * 1000),
                            "{:+.3f}".format(row["delta_s"] * 1000),
                            "n/a" if row["delta_percent"] is None else "{:+.1f}%".format(row["delta_percent"]),
                            "{:.3f}".format(row["regression_threshold_s"] * 1000),
                            row["status"],
                        )
                        for row in comparison_rows
                    ],
                ),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main():
    args = parse_args()
    rounds = 5 if args.quick else args.rounds
    cases = selected_cases(args.case)
    if not cases:
        raise SystemExit("no benchmarks matched the requested filters")

    runs = _benchmark_runs(cases)
    _run_interleaved(runs, rounds=rounds)

    rows = [
        {
            "id": run.case.benchmark_id,
            "name": run.case.expression,
            "construct": run.case.expression,
            "benchmark_id": run.case.benchmark_id,
            "description": run.case.description,
            "summary": common.summarize_samples(run.samples),
            "samples_s": run.samples,
        }
        for run in runs
    ]
    payload = {
        "schema_version": 1,
        "benchmark_id": "fast_prepared_eval",
        "benchmark_name": "Fast Benchmarks: Prepared Evaluation",
        "category": "fast",
        "environment": common.benchmark_environment(),
        "config": {
            "rounds": rounds,
            "filters": args.case,
        },
        "rows": rows,
    }
    baseline_payload = common.load_benchmark_payload(payload["benchmark_id"], "tracked")
    payload, _comparison = common.payload_with_baseline_comparison(payload, baseline_payload)

    print("Fast benchmark suite")
    print("prepared evaluation only; parsing and interpreter startup are excluded")
    print("interleaved rounds: yes")
    print("cache reuse mode: no")
    print()
    for line in common.highlight_lines(payload):
        print(f"NOTE: {line}")
    if common.highlight_lines(payload):
        print()
    print(
        common.markdown_table(
            (
                "Construct",
                "Median (ms)",
                "Mean (ms)",
                "Min (ms)",
                "Max (ms)",
                "Stdev (ms)",
                "StdErr Mean (ms)",
            ),
            [
                (
                    row["construct"],
                    "{:.3f}".format(row["summary"]["median"] * 1000),
                    "{:.3f}".format(row["summary"]["mean"] * 1000),
                    "{:.3f}".format(row["summary"]["min"] * 1000),
                    "{:.3f}".format(row["summary"]["max"] * 1000),
                    "{:.3f}".format(row["summary"]["stdev"] * 1000),
                    "{:.3f}".format(row["summary"]["stderr_mean"] * 1000),
                )
                for row in rows
            ],
        )
    )
    comparison_rows = common.comparison_rows(payload)
    if comparison_rows:
        print()
        print("Comparison against previous tracked result")
        print()
        print(
            common.markdown_table(
                ("Construct", "Current (ms)", "Tracked (ms)", "Delta (ms)", "Delta (%)", "Threshold (ms)", "Status"),
                [
                    (
                        row["construct"],
                        "{:.3f}".format(row["current_median_s"] * 1000),
                        "{:.3f}".format(row["baseline_median_s"] * 1000),
                        "{:+.3f}".format(row["delta_s"] * 1000),
                        "n/a" if row["delta_percent"] is None else "{:+.1f}%".format(row["delta_percent"]),
                        "{:.3f}".format(row["regression_threshold_s"] * 1000),
                        row["status"],
                    )
                    for row in comparison_rows
                ],
            )
        )

    artifact_paths = common.write_artifact_bundle(
        payload["benchmark_id"],
        args.output,
        payload,
        render_markdown(payload, baseline_payload=baseline_payload),
    )
    if artifact_paths is not None:
        print()
        print("Artifacts written to {} and {}".format(*artifact_paths))
    if args.fail_on_regression and common.has_regressions(payload):
        raise SystemExit("fast benchmark regression exceeded tracked threshold")


if __name__ == "__main__":
    main()
