#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
tree_id="$(git -C "$repo_root" write-tree)"
temp_root="$(mktemp -d /tmp/dice-staged-bench.XXXXXX)"

cleanup() {
    rm -rf "$temp_root"
}
trap cleanup EXIT

git -C "$repo_root" archive --format=tar "$tree_id" | tar -xf - -C "$temp_root"

run_in_tree() {
    local script_path="$1"
    shift
    (
        cd "$temp_root"
        BENCHMARK_RUN_CONTEXT="during-commit" python3 "$script_path" "$@"
    )
}

run_if_present() {
    local ran_ref="$1"
    shift
    local script_path="$1"
    shift
    if [[ ! -f "$temp_root/$script_path" ]]; then
        echo "Skipping missing benchmark entry point: $script_path"
        return 0
    fi
    printf -v "$ran_ref" '%s' "1"
    run_in_tree "$script_path" "$@"
}

fast_args=(benchmarks/fast/run.py --output tracked --fail-on-regression)
end_to_end_args=(benchmarks/end_to_end/run.py --output tracked --fail-on-regression)
slow_args=(benchmarks/slow/run.py --output tracked)
hexed_args=(benchmarks/monte_carlo_comparison/hexed_scorching_ray/run.py --output tracked --skip-validation)
chaos_args=(benchmarks/monte_carlo_comparison/chaos_bolt_chain/run.py --output tracked --skip-validation)

if [[ "${BENCHMARK_REFRESH:-0}" == "1" ]]; then
    # Refresh mode still runs the commit-time suites and writes tracked artifacts,
    # but it skips the regression gate so intentional baseline updates can land.
    fast_args=(benchmarks/fast/run.py --output tracked)
    end_to_end_args=(benchmarks/end_to_end/run.py --output tracked)
fi

if [[ "${BENCHMARK_QUICK:-0}" == "1" ]]; then
    fast_args+=(--quick)
    end_to_end_args+=(--quick)
    slow_args+=(--quick)
    hexed_args+=(--skip-validation --sample-counts 20)
    chaos_args+=(--skip-validation --sample-counts 20 --preset small)
fi

echo "Running tracked commit benchmarks from staged tree"
if [[ "${BENCHMARK_REFRESH:-0}" == "1" ]]; then
    echo "Benchmark refresh mode: regression failures are disabled for fast and end-to-end suites"
fi
ran_any=0
run_if_present ran_any "${fast_args[@]}"
run_if_present ran_any "${end_to_end_args[@]}"

if [[ "${BENCHMARK_SLOW:-0}" == "1" ]]; then
    run_if_present ran_any "${slow_args[@]}"
fi

if [[ "${BENCHMARK_MONTE_CARLO:-0}" == "1" ]]; then
    run_if_present ran_any "${hexed_args[@]}"
    run_if_present ran_any "${chaos_args[@]}"
fi

if [[ "$ran_any" != "1" ]]; then
    echo "No staged benchmark suites were available to run"
    exit 0
fi

mkdir -p "$repo_root/benchmarks/results/tracked"
cp -a "$temp_root/benchmarks/results/tracked/." "$repo_root/benchmarks/results/tracked/"
git -C "$repo_root" add benchmarks/results/tracked
