"""Shared benchmark reporting helpers."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import socket
import statistics
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "benchmarks" / "results"
OUTPUT_MODES = ("none", "local", "tracked")


def cells_dict(result) -> dict[tuple[object, ...], object]:
    return result.cells if hasattr(result, "cells") else result


def distribution_mean(distribution: dict[int, float]) -> float:
    return sum(outcome * probability for outcome, probability in distribution.items())


def total_variation_distance(exact_distribution, sampled_distribution: dict[int, float]) -> float:
    outcomes = set(sampled_distribution)
    outcomes.update(exact_distribution.keys())
    total = 0.0
    for outcome in outcomes:
        total += abs(exact_distribution[outcome] - sampled_distribution.get(outcome, 0.0))
    return total / 2.0


def summarize_cells(exact_sweep, sampled_sweep, coordinates) -> list[str]:
    lines = []
    exact_cells = cells_dict(exact_sweep)
    sampled_cells = cells_dict(sampled_sweep)
    for coordinate in coordinates:
        exact = exact_cells[coordinate]
        sampled = sampled_cells[coordinate]
        lines.append(
            "{} exact_mean={:.3f} sampled_mean={:.3f} exact_support={} sampled_support={}".format(
                coordinate,
                exact.average(),
                distribution_mean(sampled),
                len(exact.items()),
                len(sampled),
            )
        )
    return lines


def mean_absolute_error(exact_result, sampled_result, coordinates) -> float:
    exact_cells = cells_dict(exact_result)
    sampled_cells = cells_dict(sampled_result)
    errors = [
        abs(exact_cells[coordinate].average() - distribution_mean(sampled_cells[coordinate]))
        for coordinate in coordinates
    ]
    return sum(errors) / len(errors)


def sample_coordinates(backend, coordinates, trials: int, seed: int, **backend_kwargs) -> dict[tuple[object, ...], dict[int, float]]:
    sampled = {}
    for index, coordinate in enumerate(coordinates):
        sampled[coordinate] = backend.sample_coordinate_distribution(
            coordinate,
            trials,
            seed=seed + index,
            **backend_kwargs
        )
    return sampled


def markdown_table(headers, rows) -> str:
    widths = [len(header) for header in headers]
    string_rows = [[str(value) for value in row] for row in rows]
    for row in string_rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    header_line = "| " + " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)) + " |"
    separator_line = "| " + " | ".join("-" * widths[index] for index in range(len(headers))) + " |"
    row_lines = [
        "| " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(row)) + " |"
        for row in string_rows
    ]
    return "\n".join([header_line, separator_line] + row_lines)


def _git_output(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def benchmark_environment() -> dict[str, object]:
    dirty_output = _git_output("status", "--short")
    run_context = os.environ.get("BENCHMARK_RUN_CONTEXT")
    return {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "git_commit": _git_output("rev-parse", "HEAD"),
        "git_branch": _git_output("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(dirty_output),
        "run_context": run_context,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
    }


def result_paths(benchmark_id: str, output_mode: str) -> tuple[Path, Path]:
    base_dir = RESULTS_DIR / output_mode
    return base_dir / f"{benchmark_id}.json", base_dir / f"{benchmark_id}.md"


def load_benchmark_payload(benchmark_id: str, output_mode: str) -> dict[str, object] | None:
    json_path, _markdown_path = result_paths(benchmark_id, output_mode)
    if not json_path.is_file():
        return None
    return json.loads(json_path.read_text(encoding="utf-8"))


def summarize_samples(samples: list[float]) -> dict[str, float | int]:
    if not samples:
        raise ValueError("expected at least one timing sample")
    stdev = statistics.stdev(samples) if len(samples) > 1 else 0.0
    return {
        "count": len(samples),
        "median": statistics.median(samples),
        "mean": statistics.fmean(samples),
        "min": min(samples),
        "max": max(samples),
        "stdev": stdev,
        "stderr_mean": stdev / math.sqrt(len(samples)),
    }


def summary_stat(summary: dict[str, object] | None, key: str) -> float | int | None:
    if summary is None:
        return None
    if key in summary:
        return summary[key]
    if key == "stderr_mean":
        count = int(summary.get("count", 0))
        if count <= 0:
            return None
        return float(summary.get("stdev", 0.0)) / math.sqrt(count)
    return None


def write_artifact_bundle(
    benchmark_id: str,
    output_mode: str,
    payload: dict[str, object],
    markdown_text: str,
) -> tuple[Path, Path] | None:
    if output_mode == "none":
        return None
    if output_mode not in OUTPUT_MODES:
        raise ValueError("unsupported benchmark output mode {}".format(output_mode))

    json_path, markdown_path = result_paths(benchmark_id, output_mode)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown_text, encoding="utf-8")
    update_combined_report(output_mode)
    return json_path, markdown_path


def _combined_fast_rows(payload: dict[str, object]):
    return markdown_table(
        ("Benchmark", "Mode", "Median (ms)", "Mean (ms)", "Stdev (ms)", "StdErr Mean (ms)"),
        [
            (
                row["name"],
                row.get("mode", "-"),
                "{:.3f}".format(summary_stat(row["summary"], "median") * 1000),
                "{:.3f}".format(summary_stat(row["summary"], "mean") * 1000),
                "{:.3f}".format(summary_stat(row["summary"], "stdev") * 1000),
                "{:.3f}".format(summary_stat(row["summary"], "stderr_mean") * 1000),
            )
            for row in payload.get("rows", [])
        ],
    )


def _combined_slow_rows(payload: dict[str, object]):
    return markdown_table(
        ("Benchmark", "Budget (s)", "Max Scale", "Unit", "Frontier Median (s)", "Stdev (s)", "StdErr Mean (s)"),
        [
            (
                row["name"],
                "{:.2f}".format(row["budget_s"]),
                row["max_scale"],
                row["unit"],
                "n/a" if row["frontier_summary"] is None else "{:.3f}".format(summary_stat(row["frontier_summary"], "median")),
                "n/a" if row["frontier_summary"] is None else "{:.3f}".format(summary_stat(row["frontier_summary"], "stdev")),
                "n/a"
                if row["frontier_summary"] is None
                else "{:.3f}".format(summary_stat(row["frontier_summary"], "stderr_mean")),
            )
            for row in payload.get("rows", [])
        ],
    )


def _combined_end_to_end_rows(payload: dict[str, object]):
    return markdown_table(
        ("Benchmark", "Median (ms)", "Mean (ms)", "Stdev (ms)", "StdErr Mean (ms)"),
        [
            (
                row["name"],
                "{:.3f}".format(summary_stat(row["summary"], "median") * 1000),
                "{:.3f}".format(summary_stat(row["summary"], "mean") * 1000),
                "{:.3f}".format(summary_stat(row["summary"], "stdev") * 1000),
                "{:.3f}".format(summary_stat(row["summary"], "stderr_mean") * 1000),
            )
            for row in payload.get("rows", [])
        ],
    )


def _combined_monte_carlo_rows(payload: dict[str, object]):
    return markdown_table(
        ("Backend", "Samples / cell", "Scope", "Time (s)", "Stdev (s)", "StdErr Mean (s)", "vs dice", "Rep. mean abs err"),
        [_row_columns(row) for row in payload.get("rows", [])],
    )


def _combined_exploratory_rows(payload: dict[str, object]):
    return markdown_table(
        ("Step", "Cells", "Elapsed (s)", "Label"),
        [
            (
                row["scale"],
                row["cells"],
                "{:.3f}".format(row["summary"]["median"]),
                row["label"],
            )
            for row in payload.get("rows", [])
        ],
    )


def render_combined_report(output_mode: str) -> str:
    base_dir = RESULTS_DIR / output_mode
    payload_paths = sorted(path for path in base_dir.glob("*.json"))
    lines = [
        "# Benchmark Report ({})".format(output_mode),
        "",
    ]
    if not payload_paths:
        lines.append("No benchmark artifacts present.\n")
        return "\n".join(lines)

    for path in payload_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        lines.append("## {}".format(payload.get("benchmark_name", path.stem)))
        lines.append("")
        environment = payload.get("environment", {})
        if environment:
            context_suffix = ""
            if environment.get("run_context"):
                context_suffix = " [{}]".format(environment["run_context"])
            lines.append(
                "Run: commit `{}` on `{}` at {}{}{}".format(
                    environment.get("git_commit", "unknown"),
                    environment.get("hostname", "unknown"),
                    environment.get("timestamp", "unknown"),
                    context_suffix,
                    " (dirty)" if environment.get("git_dirty") else "",
                )
            )
            lines.append("")
        category = payload.get("category")
        if category == "fast":
            lines.append(_combined_fast_rows(payload))
        elif category == "slow":
            lines.append(_combined_slow_rows(payload))
        elif category == "end_to_end":
            lines.append(_combined_end_to_end_rows(payload))
        elif category == "monte_carlo_comparison":
            lines.append(_combined_monte_carlo_rows(payload))
        elif category == "exploratory":
            lines.append(_combined_exploratory_rows(payload))
        else:
            lines.append("Unknown benchmark payload schema.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_combined_report(output_mode: str) -> None:
    if output_mode == "none":
        return
    base_dir = RESULTS_DIR / output_mode
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "latest.md").write_text(render_combined_report(output_mode), encoding="utf-8")


def _display_samples(value) -> str:
    return "-" if value in (None, "-") else "{:,}".format(value)


def _display_ratio(value: float) -> str:
    return "<0.01x" if value < 0.01 else "{:.2f}x".format(value)


def _row_summary(row: dict[str, object]) -> dict[str, float | int]:
    summary = row.get("summary")
    if summary is not None:
        if "stderr_mean" not in summary:
            summary = dict(summary)
            summary["stderr_mean"] = summary_stat(summary, "stderr_mean") or 0.0
        return summary
    return summarize_samples([float(row["elapsed_s"])])


def _row_columns(row: dict[str, object]) -> tuple[str, str, str, str, str, str, str, str]:
    summary = _row_summary(row)
    return (
        str(row["backend"]),
        _display_samples(row.get("samples_per_cell")),
        str(row["scope"]),
        "{:.3f}".format(summary["median"]),
        "{:.3f}".format(summary["stdev"]),
        "{:.3f}".format(summary["stderr_mean"]),
        _display_ratio(row["vs_exact"]),
        "{:.4f}".format(row["rep_mean_abs_error"]),
    )


def _comparison_rows(current_payload: dict[str, object], baseline_payload: dict[str, object]) -> list[tuple[str, str, str, str, str]]:
    baseline_by_id = {
        row["id"]: row
        for row in baseline_payload.get("rows", [])
    }
    rows = []
    for row in current_payload.get("rows", []):
        baseline = baseline_by_id.get(row["id"])
        if baseline is None:
            continue
        current_elapsed = row["elapsed_s"]
        baseline_elapsed = baseline["elapsed_s"]
        delta = current_elapsed - baseline_elapsed
        delta_percent = (delta / baseline_elapsed * 100.0) if baseline_elapsed else None
        rows.append(
            (
                str(row["backend"]),
                "{:.3f}".format(current_elapsed),
                "{:.3f}".format(baseline_elapsed),
                "{:+.3f}".format(delta),
                "n/a" if delta_percent is None else "{:+.1f}%".format(delta_percent),
            )
        )
    return rows


def render_benchmark_markdown(
    payload: dict[str, object],
    baseline_payload: dict[str, object] | None = None,
) -> str:
    lines = [
        "# {}".format(payload["benchmark_name"]),
        "",
    ]

    summary_lines = payload.get("summary_lines", [])
    if summary_lines:
        for line in summary_lines:
            lines.append("- {}".format(line))
        lines.append("")

    environment = payload.get("environment", {})
    lines.extend(
        [
            "## Run Metadata",
            "",
            "- timestamp: {}".format(environment.get("timestamp", "unknown")),
            "- git commit: {}".format(environment.get("git_commit", "unknown")),
            "- git branch: {}".format(environment.get("git_branch", "unknown")),
            "- run context: {}".format(environment.get("run_context", "normal")),
            "- worktree dirty: {}".format("yes" if environment.get("git_dirty") else "no"),
            "- host: {}".format(environment.get("hostname", "unknown")),
            "- platform: {}".format(environment.get("platform", "unknown")),
            "- python: {}".format(environment.get("python_version", "unknown")),
            "",
            "## Current Results",
            "",
            markdown_table(
                (
                    "Backend",
                    "Samples / cell",
                    "Scope",
                    "Time (s)",
                    "Stdev (s)",
                    "StdErr Mean (s)",
                    "vs dice",
                    "Rep. mean abs err",
                ),
                [_row_columns(row) for row in payload.get("rows", [])],
            ),
            "",
        ]
    )

    representative_lines = payload.get("representative_lines", [])
    if representative_lines:
        lines.extend(["## Representative Cells", ""])
        for run in representative_lines:
            lines.append("### {}".format(run["label"]))
            lines.append("")
            for line in run["lines"]:
                lines.append("- {}".format(line))
            lines.append("")

    if baseline_payload is not None:
        comparison_rows = _comparison_rows(payload, baseline_payload)
        if comparison_rows:
            lines.extend(
                [
                    "## Comparison Against Tracked Baseline",
                    "",
                    markdown_table(
                        ("Backend", "Current (s)", "Tracked (s)", "Delta (s)", "Delta (%)"),
                        comparison_rows,
                    ),
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def write_benchmark_artifacts(payload: dict[str, object], output_mode: str) -> tuple[Path, Path] | None:
    if output_mode == "none":
        return None
    if output_mode not in OUTPUT_MODES:
        raise ValueError("unsupported benchmark output mode {}".format(output_mode))

    json_path, markdown_path = result_paths(payload["benchmark_id"], output_mode)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    baseline_payload = None
    if output_mode == "local":
        baseline_payload = load_benchmark_payload(payload["benchmark_id"], "tracked")

    write_artifact_bundle(
        payload["benchmark_id"],
        output_mode,
        payload,
        render_benchmark_markdown(payload, baseline_payload=baseline_payload),
    )
    return json_path, markdown_path
