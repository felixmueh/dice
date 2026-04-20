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
    from benchmarks.slow.cases import CASES
else:
    from benchmarks import common
    from benchmarks.slow.cases import CASES


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        choices=common.OUTPUT_MODES,
        default="local",
        help="Write benchmark artifacts to benchmarks/results/<mode>/.",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=1.0,
        help="Wall-clock budget in seconds for frontier search.",
    )
    parser.add_argument("--rounds", type=int, default=1, help="Timed samples per candidate scale.")
    parser.add_argument("--warmups", type=int, default=0, help="Untimed warmup samples per candidate scale.")
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        help="Substring filter for benchmark ids. May be passed multiple times.",
    )
    parser.add_argument("--quick", action="store_true", help="Use a tiny smoke-test budget and sample count.")
    return parser.parse_args()


def selected_cases(filters):
    if not filters:
        return CASES
    normalized = tuple(value.lower() for value in filters)
    return tuple(case for case in CASES if any(value in case.benchmark_id.lower() for value in normalized))


def measure_scale(case, scale: int, warmups: int, rounds: int):
    point = case.point(scale)
    instance = case.build_instance(scale)
    for _ in range(warmups):
        instance.reset()
        instance.run_once()
    samples = []
    for _ in range(rounds):
        instance.reset()
        start = perf_counter()
        instance.run_once()
        samples.append(perf_counter() - start)
    return {
        "scale": scale,
        "point_label": point.label,
        "cells": point.cells,
        "samples_s": samples,
        "summary": common.summarize_samples(samples),
    }


def _row_id(case, budget: float) -> str:
    return "{}:{:.3f}".format(case.benchmark_id, budget)


def _previous_payload(output_mode: str):
    payload = common.load_benchmark_payload("slow_frontier", output_mode)
    if payload is not None:
        return payload
    if output_mode != "tracked":
        return common.load_benchmark_payload("slow_frontier", "tracked")
    return None


def _previous_scale(previous_payload, case, budget: float):
    if previous_payload is None:
        return None
    previous_by_id = {row["id"]: row for row in previous_payload.get("rows", [])}
    previous_row = previous_by_id.get(_row_id(case, budget))
    if previous_row is None:
        return None
    scale = int(previous_row.get("max_scale", 0))
    if scale <= 0:
        return None
    return min(case.max_scale, scale)


def frontier_for_budget(case, budget: float, warmups: int, rounds: int, previous_scale: int | None = None):
    measurements = {}

    def measurement(scale: int):
        scale = max(1, min(case.max_scale, scale))
        if scale not in measurements:
            measurements[scale] = measure_scale(case, scale, warmups=warmups, rounds=rounds)
        return measurements[scale]

    best = None
    first_fail = None

    if previous_scale is not None:
        anchor = max(1, min(case.max_scale, previous_scale))
        anchor_result = measurement(anchor)
        if anchor_result["summary"]["median"] <= budget:
            best = anchor_result
            low = anchor + 1
            upper = None
            candidate = min(case.max_scale, max(anchor + 1, anchor * 2))
            while candidate <= case.max_scale:
                candidate_result = measurement(candidate)
                if candidate_result["summary"]["median"] <= budget:
                    best = candidate_result
                    if candidate == case.max_scale:
                        return best, None, measurements
                    low = candidate + 1
                    next_candidate = min(case.max_scale, candidate * 2)
                    if next_candidate == candidate:
                        break
                    candidate = next_candidate
                    continue
                first_fail = candidate_result
                upper = candidate - 1
                break
            if upper is None:
                return best, first_fail, measurements
            high = upper
        else:
            first_fail = anchor_result
            high = anchor - 1
            candidate = max(1, anchor // 2)
            while True:
                candidate_result = measurement(candidate)
                if candidate_result["summary"]["median"] <= budget:
                    best = candidate_result
                    low = candidate + 1
                    break
                first_fail = candidate_result
                if candidate == 1:
                    return None, first_fail, measurements
                high = candidate - 1
                candidate = max(1, candidate // 2)
                if candidate > high:
                    candidate = high
    else:
        candidate = 1
        while candidate <= case.max_scale:
            candidate_result = measurement(candidate)
            if candidate_result["summary"]["median"] <= budget:
                best = candidate_result
                if candidate == case.max_scale:
                    return best, None, measurements
                next_candidate = min(case.max_scale, candidate * 2)
                low = candidate + 1
                if next_candidate == candidate:
                    break
                candidate = next_candidate
                continue
            first_fail = candidate_result
            high = candidate - 1
            break
        else:
            return best, first_fail, measurements

        if best is None:
            return None, first_fail, measurements

    while low <= high:
        mid = (low + high) // 2
        result = measurement(mid)
        if result["summary"]["median"] <= budget:
            best = result
            low = mid + 1
        else:
            first_fail = result
            high = mid - 1
    return best, first_fail, measurements


def _comparison_rows(payload, baseline_payload):
    if baseline_payload is None:
        return []
    baseline_by_id = {row["id"]: row for row in baseline_payload.get("rows", [])}
    rows = []
    for row in payload["rows"]:
        baseline = baseline_by_id.get(row["id"])
        if baseline is None:
            continue
        delta = row["frontier_cells"] - baseline.get("frontier_cells", 0)
        delta_percent = (delta / baseline["frontier_cells"] * 100.0) if baseline.get("frontier_cells") else None
        rows.append(
            (
                row["name"],
                "{:.2f}".format(row["budget_s"]),
                row["frontier_cells"],
                baseline.get("frontier_cells", 0),
                "{:+d}".format(delta),
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
        "- budget (s): {:.2f}".format(payload["config"]["budget_s"]),
        "- timed samples per candidate: {}".format(payload["config"]["rounds"]),
        "- warmup samples per candidate: {}".format(payload["config"]["warmups"]),
        "- parsing included: no",
        "- interpreter startup included: no",
        "- cache mode: cold",
        "",
        "## Results",
        "",
        common.markdown_table(
            (
                "Benchmark",
                "Budget (s)",
                "Frontier Cells",
                "Frontier Point",
                "Frontier Median (s)",
                "Stdev (s)",
                "StdErr Mean (s)",
                "First Fail",
            ),
            [
                (
                    row["name"],
                    "{:.2f}".format(row["budget_s"]),
                    row["frontier_cells"],
                    row["frontier_point"],
                    "{:.3f}".format(row["frontier_summary"]["median"]) if row["frontier_summary"] is not None else "n/a",
                    "{:.3f}".format(row["frontier_summary"]["stdev"]) if row["frontier_summary"] is not None else "n/a",
                    "{:.3f}".format(row["frontier_summary"]["stderr_mean"])
                    if row["frontier_summary"] is not None
                    else "n/a",
                    row["first_fail_point"] if row["first_fail_point"] is not None else "-",
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
                    ("Benchmark", "Budget (s)", "Current Cells", "Tracked Cells", "Delta", "Delta (%)"),
                    comparison_rows,
                ),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main():
    args = parse_args()
    budget = 0.05 if args.quick else args.budget
    rounds = 1 if args.quick else args.rounds
    warmups = 0 if args.quick else args.warmups
    cases = selected_cases(args.case)
    if not cases:
        raise SystemExit("no benchmarks matched the requested filters")
    previous_payload = _previous_payload(args.output)

    rows = []
    print("Slow benchmark suite")
    print("budget-frontier search over prepared exact sweeps")
    print()
    for case in cases:
        previous_scale = _previous_scale(previous_payload, case, budget)
        best, first_fail, _measurements = frontier_for_budget(
            case,
            budget,
            warmups=warmups,
            rounds=rounds,
            previous_scale=previous_scale,
        )
        rows.append(
            {
                "id": _row_id(case, budget),
                "name": case.name,
                "benchmark_id": case.benchmark_id,
                "budget_s": budget,
                "unit": case.unit,
                "search_start_scale": previous_scale,
                "max_scale": best["scale"] if best is not None else 0,
                "frontier_cells": 0 if best is None else best["cells"],
                "frontier_point": None if best is None else best["point_label"],
                "frontier_summary": None if best is None else best["summary"],
                "frontier_samples_s": [] if best is None else best["samples_s"],
                "first_fail_scale": None if first_fail is None else first_fail["scale"],
                "first_fail_cells": None if first_fail is None else first_fail["cells"],
                "first_fail_point": None if first_fail is None else first_fail["point_label"],
                "first_fail_summary": None if first_fail is None else first_fail["summary"],
            }
        )
        print(
            "{} @ {:.2f}s -> max {} cells ({}){}".format(
                case.name,
                budget,
                0 if best is None else best["cells"],
                "-" if best is None else best["point_label"],
                "" if previous_scale is None else " (started from {})".format(previous_scale),
            )
        )

    payload = {
        "schema_version": 1,
        "benchmark_id": "slow_frontier",
        "benchmark_name": "Slow Benchmarks: Budget Frontier",
        "category": "slow",
        "environment": common.benchmark_environment(),
        "config": {
            "budget_s": budget,
            "rounds": rounds,
            "warmups": warmups,
            "filters": args.case,
        },
        "rows": rows,
    }
    baseline_payload = common.load_benchmark_payload(payload["benchmark_id"], "tracked") if args.output == "local" else None
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
