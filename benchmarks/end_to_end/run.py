#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from time import perf_counter


if __package__ in (None, ""):
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from benchmarks import common
    from benchmarks.end_to_end.cases import CASES, ROOT as CASES_ROOT
    from dice import interpret_statement
else:
    from benchmarks import common
    from benchmarks.end_to_end.cases import CASES, ROOT as CASES_ROOT
    from dice import interpret_statement


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        choices=common.OUTPUT_MODES,
        default="local",
        help="Write benchmark artifacts to benchmarks/results/<mode>/.",
    )
    parser.add_argument("--rounds", type=int, default=9, help="Timed rounds per benchmark.")
    parser.add_argument("--warmups", type=int, default=2, help="Untimed warmup rounds.")
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        help="Substring filter for benchmark ids. May be passed multiple times.",
    )
    parser.add_argument("--quick", action="store_true", help="Run fewer rounds for a smoke test.")
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit non-zero if a tracked-baseline regression exceeds the configured threshold.",
    )
    return parser.parse_args()


def selected_cases(filters):
    if not filters:
        return CASES
    normalized = tuple(value.lower() for value in filters)
    return tuple(case for case in CASES if any(value in case.benchmark_id.lower() for value in normalized))


def _time_once(case):
    start = perf_counter()
    interpret_statement(case.program, current_dir=str(CASES_ROOT), source_name=f"<benchmark:{case.benchmark_id}>")
    return perf_counter() - start


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
            "- warmup rounds: {}".format(payload["config"]["warmups"]),
            "- parsing included: yes",
            "- interpreter startup included: yes",
            "- session reuse: no",
            "",
            "## Results",
            "",
            common.markdown_table(
            (
                "Benchmark",
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
                    row["name"],
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
                    ("Benchmark", "Current (ms)", "Tracked (ms)", "Delta (ms)", "Delta (%)", "Threshold (ms)", "Status"),
                    [
                        (
                            row["name"],
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
    rounds = 3 if args.quick else args.rounds
    warmups = 1 if args.quick else args.warmups
    cases = selected_cases(args.case)
    if not cases:
        raise SystemExit("no benchmarks matched the requested filters")

    for _ in range(warmups):
        for case in cases:
            _time_once(case)

    rows = []
    for case in cases:
        samples = []
        for _ in range(rounds):
            samples.append(_time_once(case))
        rows.append(
            {
                "id": case.benchmark_id,
                "name": case.name,
                "benchmark_id": case.benchmark_id,
                "description": case.description,
                "summary": common.summarize_samples(samples),
                "samples_s": samples,
            }
        )

    payload = {
        "schema_version": 1,
        "benchmark_id": "end_to_end_wall_clock",
        "benchmark_name": "End-to-End Benchmarks",
        "category": "end_to_end",
        "environment": common.benchmark_environment(),
        "config": {
            "rounds": rounds,
            "warmups": warmups,
            "filters": args.case,
        },
        "rows": rows,
    }
    baseline_payload = common.load_benchmark_payload(payload["benchmark_id"], "tracked")
    payload, _comparison = common.payload_with_baseline_comparison(payload, baseline_payload)

    print("End-to-end benchmark suite")
    print("parsing and interpreter startup are included")
    print()
    for line in common.highlight_lines(payload):
        print(f"NOTE: {line}")
    if common.highlight_lines(payload):
        print()
    print(
        common.markdown_table(
            (
                "Benchmark",
                "Median (ms)",
                "Mean (ms)",
                "Min (ms)",
                "Max (ms)",
                "Stdev (ms)",
                "StdErr Mean (ms)",
            ),
            [
                (
                    row["name"],
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
                ("Benchmark", "Current (ms)", "Tracked (ms)", "Delta (ms)", "Delta (%)", "Threshold (ms)", "Status"),
                [
                    (
                        row["name"],
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
        raise SystemExit("end-to-end benchmark regression exceeded tracked threshold")


if __name__ == "__main__":
    main()
