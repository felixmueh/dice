import json
import math
import os
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path
from numbers import Real


ROOT = Path(__file__).resolve().parents[1]

os.environ.setdefault("MPLBACKEND", "Agg")
mpl_config = Path(tempfile.gettempdir()) / "dice-mplconfig"
mpl_config.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dice import interpret_file, interpret_statement
from dice.cli import _serialize_result
from dice.diceengine import SweepValues
from tests.json_regression_cases import all_cases


FLOAT_REL_TOLERANCE = 1e-9
FLOAT_ABS_TOLERANCE = 1e-12


def _normalize_snapshot_payload(payload):
    if payload.get("type") == "string":
        value = payload.get("value")
        if isinstance(value, str) and value.startswith("/tmp/dice-render-") and value.endswith(".png"):
            normalized = dict(payload)
            normalized["value"] = "__RENDER_OUTPUT__"
            return normalized
    return payload


def _is_real_number(value):
    return isinstance(value, Real) and not isinstance(value, bool)


def _float_like(left, right):
    return _is_real_number(left) and _is_real_number(right) and (
        isinstance(left, float) or isinstance(right, float)
    )


def evaluate_case(case):
    SweepValues.counter = 0
    if case.mode == "python":
        path = Path(case.source)
        module_name = "_dice_sample_" + "_".join(path.relative_to(ROOT).with_suffix("").parts)
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise AssertionError(f"could not load python sample {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
            build_result = getattr(module, "build_result", None)
            if not callable(build_result):
                raise AssertionError(f"python sample {path} must define build_result()")
            return build_result()
        finally:
            sys.modules.pop(module_name, None)
    if case.mode == "file":
        return interpret_file(case.source, current_dir=case.current_dir, source_name=case.name)
    return interpret_statement(case.source, current_dir=case.current_dir, source_name=case.name)


class JsonRegressionTest(unittest.TestCase):
    def assertSnapshotEqual(self, actual, expected, path="root"):
        if _float_like(actual, expected):
            self.assertTrue(
                math.isclose(
                    actual,
                    expected,
                    rel_tol=FLOAT_REL_TOLERANCE,
                    abs_tol=FLOAT_ABS_TOLERANCE,
                ),
                f"{path}: {actual!r} != {expected!r} within tolerance",
            )
            return

        if type(actual) is not type(expected):
            self.fail(
                f"{path}: type mismatch {type(actual).__name__} != {type(expected).__name__}"
            )

        if isinstance(actual, dict):
            self.assertEqual(set(actual), set(expected), f"{path}: key mismatch")
            for key in actual:
                self.assertSnapshotEqual(actual[key], expected[key], f"{path}.{key}")
            return

        if isinstance(actual, list):
            self.assertEqual(len(actual), len(expected), f"{path}: length mismatch")
            for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
                self.assertSnapshotEqual(actual_item, expected_item, f"{path}[{index}]")
            return

        self.assertEqual(actual, expected, f"{path}: value mismatch")

    def test_snapshot_comparison_allows_small_float_drift(self):
        self.assertSnapshotEqual(
            {"probability": 0.30000000000000004, "entries": [1.0, 2.0 / 3.0]},
            {"probability": 0.3, "entries": [1.0, 0.6666666666666666]},
        )

    def test_snapshot_comparison_still_rejects_meaningful_float_changes(self):
        with self.assertRaises(AssertionError):
            self.assertSnapshotEqual(
                {"probability": 0.31},
                {"probability": 0.3},
            )

    def test_snapshots_match(self):
        cases = all_cases()
        self.assertTrue(cases, "expected at least one JSON regression case")

        for case in cases:
            with self.subTest(case=case.name):
                self.assertTrue(
                    case.snapshot_path.is_file(),
                    f"missing snapshot file {case.snapshot_path}",
                )
                result = evaluate_case(case)
                actual = _normalize_snapshot_payload(_serialize_result(result, probability_mode="raw"))
                expected = _normalize_snapshot_payload(json.loads(case.snapshot_path.read_text(encoding="utf-8")))
                self.assertSnapshotEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
