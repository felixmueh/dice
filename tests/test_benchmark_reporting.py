import unittest

from benchmarks import common


def _payload(median, stderr=0.0, benchmark_id="suite", row_id="case"):
    return {
        "benchmark_id": benchmark_id,
        "benchmark_name": benchmark_id,
        "rows": [
            {
                "id": row_id,
                "name": row_id,
                "summary": {
                    "median": median,
                    "mean": median,
                    "min": median,
                    "max": median,
                    "stdev": 0.0,
                    "stderr_mean": stderr,
                    "count": 5,
                },
            }
        ],
    }


class BenchmarkReportingTest(unittest.TestCase):
    def test_regression_threshold_uses_at_least_ten_percent(self):
        baseline = _payload(1.0, stderr=0.01)
        current = _payload(1.09, stderr=0.01)
        comparison = common.compare_against_baseline(current, baseline)
        self.assertIsNotNone(comparison)
        row = comparison["rows"][0]
        self.assertEqual(row["status"], "stable")
        self.assertAlmostEqual(row["regression_threshold_s"], 0.1)

        current = _payload(1.11, stderr=0.01)
        comparison = common.compare_against_baseline(current, baseline)
        self.assertEqual(comparison["rows"][0]["status"], "regression")

    def test_regression_threshold_uses_larger_stderr_when_needed(self):
        baseline = _payload(1.0, stderr=0.25)
        current = _payload(1.20, stderr=0.05)
        comparison = common.compare_against_baseline(current, baseline)
        row = comparison["rows"][0]
        self.assertAlmostEqual(row["regression_threshold_s"], 0.25)
        self.assertEqual(row["status"], "stable")

    def test_improvements_and_highlights_are_reported(self):
        baseline = _payload(1.0, stderr=0.01)
        current = _payload(0.70, stderr=0.01)
        payload, comparison = common.payload_with_baseline_comparison(current, baseline)
        self.assertIsNotNone(comparison)
        self.assertEqual(comparison["rows"][0]["status"], "improvement")
        highlights = common.highlight_lines(payload)
        self.assertEqual(len(highlights), 1)
        self.assertIn("improvement", highlights[0])


if __name__ == "__main__":
    unittest.main()
