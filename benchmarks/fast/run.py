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
    mode: str
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
    parser.add_argument("--rounds", type=int, default=9, help="Timed rounds per benchmark.")
    parser.add_argument("--warmups", type=int, default=2, help="Untimed warmup rounds.")
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
        for mode in case.modes:
            instance = case.build()
            if mode == "warm":
                instance.run_once()
            runs.append(PreparedRun(case=case, mode=mode, instance=instance, samples=[]))
    return runs


def _time_once(run: PreparedRun) -> float:
    if run.mode == "cold":
        run.instance.reset()
    start = perf_counter()
    run.instance.run_once()
    return perf_counter() - start


def _run_interleaved(runs, warmups: int, rounds: int):
    for _ in range(warmups):
        for run in runs:
            _time_once(run)
    for _ in range(rounds):
        for run in runs:
            run.samples.append(_time_once(run))


def _comparison_rows(payload, baseline_payload):
    if baseline_payload is None:
        return []
    baseline_by_id = {row["id"]: row for row in baseline_payload.get("rows", [])}
    rows = []
    for row in payload["rows"]:
        baseline = baseline_by_id.get(row["id"])
        if baseline is None:
            continue
        current = row["summary"]["median"]
        previous = baseline["summary"]["median"]
        delta = current - previous
        delta_percent = (delta / previous * 100.0) if previous else None
        rows.append(
            (
                row["name"],
                row["mode"],
                "{:.3f}".format(current * 1000),
                "{:.3f}".format(previous * 1000),
                "{:+.3f}".format(delta * 1000),
                "n/a" if delta_percent is None else "{:+.1f}%".format(delta_percent),
            )
        )
    return rows


def render_markdown(payload, baseline_payload=None):
    lines = [
        "# {}".format(payload["benchmark_name"]),
        "",
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
        "- interleaved execution: yes",
        "- parsing included: no",
        "- interpreter startup included: no",
        "",
        "## Results",
        "",
        common.markdown_table(
            (
                "Benchmark",
                "Mode",
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
                    row["mode"],
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

    comparison_rows = _comparison_rows(payload, baseline_payload)
    if comparison_rows:
        lines.extend(
            [
                "## Comparison Against Tracked Baseline",
                "",
                common.markdown_table(
                    ("Benchmark", "Mode", "Current (ms)", "Tracked (ms)", "Delta (ms)", "Delta (%)"),
                    comparison_rows,
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

    runs = _benchmark_runs(cases)
    _run_interleaved(runs, warmups=warmups, rounds=rounds)

    rows = [
        {
            "id": "{}:{}".format(run.case.benchmark_id, run.mode),
            "name": run.case.name,
            "benchmark_id": run.case.benchmark_id,
            "mode": run.mode,
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
            "warmups": warmups,
            "filters": args.case,
        },
        "rows": rows,
    }
    baseline_payload = common.load_benchmark_payload(payload["benchmark_id"], "tracked") if args.output == "local" else None

    print("Fast benchmark suite")
    print("prepared evaluation only; parsing and interpreter startup are excluded")
    print("interleaved rounds: yes")
    print()
    print(
        common.markdown_table(
            (
                "Benchmark",
                "Mode",
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
                    row["mode"],
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

    artifact_paths = common.write_artifact_bundle(
        payload["benchmark_id"],
        args.output,
        payload,
        render_markdown(payload, baseline_payload=baseline_payload),
    )
    if artifact_paths is not None:
        print()
        print("Artifacts written to {} and {}".format(*artifact_paths))


if __name__ == "__main__":
    main()
