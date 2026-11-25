import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]

os.environ.setdefault("MPLBACKEND", "Agg")
mpl_config = Path(tempfile.gettempdir()) / "dice-mplconfig"
mpl_config.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dice import D, dice_interpreter, dicefunction
from dice.diceengine import Distribution, FiniteMeasure, TRUE, FALSE, Sweep
from dice.executor import ExactExecutor
from dice.hostfunctions import get_dicefunction_metadata


def only_distribution(result):
    if isinstance(result, Sweep):
        assert result.is_unswept()
        result = result.only_value()
    assert isinstance(result, (Distribution, FiniteMeasure))
    return result


class PythonIntegrationTest(unittest.TestCase):
    def _count_invalidation_calls(self, session, callback):
        with mock.patch.object(
            session.interpreter,
            "invalidate_caches",
            wraps=session.interpreter.invalidate_caches,
        ) as invalidate:
            result = callback()
        return result, invalidate.call_count

    def test_session_accepts_explicit_executor(self):
        session = dice_interpreter(executor=ExactExecutor())
        result = only_distribution(session("1 + 1"))
        self.assertEqual(result[2], 1)

    def test_session_persists_assigned_runtime_values(self):
        session = dice_interpreter()
        result = session("d20 >= 11")
        session.assign("cached", result)
        cached = only_distribution(session("cached"))
        self.assertAlmostEqual(cached[TRUE], 0.5)
        self.assertAlmostEqual(cached[FALSE], 0.5)

    def test_session_assign_allows_global_reassignment(self):
        session = dice_interpreter()
        session.assign("cached", 1)
        self.assertEqual(session.assign("cached", 2), 2)
        self.assertEqual(session("cached"), 2)

    def test_registers_decorated_python_function(self):
        session = dice_interpreter()

        @dicefunction
        def add_bonus(value, bonus=2):
            return value + bonus

        session.register_function(add_bonus)
        self.assertEqual(session("add_bonus(3)"), 5)
        self.assertEqual(session("add_bonus(bonus=4, value=3)"), 7)

    def test_registers_decorated_distribution_function(self):
        session = dice_interpreter()

        @dicefunction
        def increment(value: Distribution) -> Distribution:
            return Distribution((outcome + 1, probability) for outcome, probability in value.items())

        session.register_function(increment)
        result = session("increment([1..2])")
        self.assertEqual(result.axes[0].values, (1, 2))
        self.assertEqual(result.cells[(1,)][2], 1)
        self.assertEqual(result.cells[(2,)][3], 1)

    def test_decorated_function_lifts_when_called_directly_from_python(self):
        session = dice_interpreter()

        @dicefunction
        def add_two(value):
            return value + 2

        result = add_two(session("[1..3]"))
        self.assertEqual(result.axes[0].values, (1, 2, 3))
        self.assertEqual(result.cells[(1,)], 3)
        self.assertEqual(result.cells[(2,)], 4)
        self.assertEqual(result.cells[(3,)], 5)

    def test_direct_python_and_dice_calls_match_for_decorated_function(self):
        session = dice_interpreter()

        @dicefunction
        def add_two(value):
            return value + 2

        session.register_function(add_two)
        dice_result = session("add_two([1..3])")
        direct_result = add_two(session("[1..3]"))
        self.assertEqual(str(dice_result), str(direct_result))

    def test_duplicate_registered_name_raises(self):
        session = dice_interpreter()

        @dicefunction(name="alias")
        def first(value):
            return value

        @dicefunction(name="alias")
        def second(value):
            return value

        session.register_function(first)
        with self.assertRaisesRegex(Exception, "Duplicate function definition"):
            session.register_function(second)

    def test_register_function_rejects_undecorated_callable(self):
        session = dice_interpreter()

        def add_bonus(value):
            return value + 2

        with self.assertRaisesRegex(Exception, "@dicefunction"):
            session.register_function(add_bonus)

    def test_decorator_name_override_registers_alias(self):
        session = dice_interpreter()

        @dicefunction(name="alias")
        def add_bonus(value):
            return value + 2

        session.register_function(add_bonus)
        self.assertEqual(session("alias(3)"), 5)

    def test_assign_rejects_unsupported_python_values(self):
        session = dice_interpreter()
        with self.assertRaisesRegex(Exception, "Unsupported host value type"):
            session.assign("bad", object())

    def test_registered_function_rejects_unsupported_return_type(self):
        session = dice_interpreter()

        @dicefunction
        def bad():
            return object()

        session.register_function(bad)
        with self.assertRaisesRegex(Exception, "Unsupported host value type"):
            session("bad()")

    def test_registered_function_supports_dice_expression_defaults(self):
        session = dice_interpreter()
        session.assign("default_bonus", 3)

        @dicefunction
        def add_default_bonus(value, bonus=D("default_bonus")):
            return value + bonus

        session.register_function(add_default_bonus)
        self.assertEqual(session("add_default_bonus(4)"), 7)

    def test_decorated_function_rejects_d_defaults_that_reference_parameters(self):
        with self.assertRaisesRegex(Exception, "D\\(\\.\\.\\.\\) defaults may only reference globals, not parameters"):
            @dicefunction
            def bad(value, bonus=D("value + 1")):
                return value + bonus

    def test_decorated_function_rejects_keyword_only_parameters(self):
        with self.assertRaisesRegex(Exception, "POSITIONAL_OR_KEYWORD"):
            @dicefunction
            def keyword_only(value, *, bonus=1):
                return value + bonus

    def test_direct_python_call_rejects_unresolved_d_defaults(self):
        @dicefunction
        def add_default_bonus(value, bonus=D("default_bonus")):
            return value + bonus

        with self.assertRaisesRegex(Exception, "dice-session invocation"):
            add_default_bonus(4)

    def test_pure_function_reuses_pure_results(self):
        calls = []

        @dicefunction(pure=True)
        def add_bonus(value, bonus=2):
            calls.append((value, bonus))
            return value + bonus

        self.assertEqual(add_bonus(3), 5)
        self.assertEqual(add_bonus(3), 5)
        self.assertEqual(calls, [(3, 2)])

    def test_pure_sweep_function_is_marked_pure_but_not_memoized(self):
        @dicefunction(pure=True)
        def summed(value: Sweep[int]):
            return value

        metadata = get_dicefunction_metadata(summed)
        self.assertTrue(metadata.pure)
        self.assertFalse(metadata.memoized)
        self.assertIsNone(metadata.cache_clear)

    def test_dsl_function_caches_pure_exact_results(self):
        session = dice_interpreter()
        session("double(value): value + value")
        self.assertEqual(only_distribution(session("double(3)"))[6], 1)
        self.assertEqual(len(session.interpreter._function_cache), 1)
        self.assertEqual(only_distribution(session("double(3)"))[6], 1)
        self.assertEqual(len(session.interpreter._function_cache), 1)

    def test_dsl_function_caches_bound_sweep_results_under_current_semantics(self):
        session = dice_interpreter()
        session("values = [a:1..2]\ndouble(value): value + value")
        first = session("double(values)")
        self.assertEqual(first.cells[(1,)][2], 1)
        self.assertEqual(len(session.interpreter._function_cache), 1)
        second = session("double(values)")
        self.assertEqual(second.cells[(2,)][4], 1)
        self.assertEqual(len(session.interpreter._function_cache), 1)

    def test_dsl_function_fresh_sweep_literals_use_current_binding_identity(self):
        session = dice_interpreter()
        session("double(value): value + value")
        session("double([a:1..2])")
        self.assertEqual(len(session.interpreter._function_cache), 1)
        session("double([a:1..2])")
        self.assertEqual(len(session.interpreter._function_cache), 2)

    def test_dsl_function_cache_is_invalidated_by_global_reassignment(self):
        session = dice_interpreter()
        session("bonus = 1\nwith_bonus(value): value + bonus")
        self.assertEqual(only_distribution(session("with_bonus(3)"))[4], 1)
        self.assertEqual(len(session.interpreter._function_cache), 1)
        session("bonus = 2")
        self.assertEqual(len(session.interpreter._function_cache), 0)
        self.assertEqual(only_distribution(session("with_bonus(3)"))[5], 1)

    def test_dsl_function_sampling_in_body_is_executable_but_not_cached(self):
        session = dice_interpreter()
        session("sample_once(): !d6")
        first = only_distribution(session("sample_once()"))
        second = only_distribution(session("sample_once()"))
        self.assertEqual(first.total_weight, 1.0)
        self.assertEqual(second.total_weight, 1.0)
        self.assertEqual(len(first.entries), 1)
        self.assertEqual(len(second.entries), 1)
        self.assertEqual(len(session.interpreter._function_cache), 0)

    def test_dsl_function_impure_host_call_in_body_is_executable_but_not_cached(self):
        session = dice_interpreter()
        session('mutate(): set_render_mode("blocking")')
        self.assertEqual(session("mutate()"), "blocking")
        self.assertEqual(session("mutate()"), "blocking")
        self.assertEqual(len(session.interpreter._function_cache), 0)

    def test_registered_impure_host_function_taints_dsl_caller(self):
        session = dice_interpreter()
        calls = []

        @dicefunction
        def impure(value):
            calls.append(value)
            return value + 1

        session.register_function(impure)
        session("wrapper(value): impure(value)")
        self.assertEqual(session("wrapper(3)"), 4)
        self.assertEqual(session("wrapper(3)"), 4)
        self.assertEqual(calls, [3, 3])
        self.assertEqual(len(session.interpreter._function_cache), 0)

    def test_session_invalidate_caches_clears_host_function_memoization(self):
        session = dice_interpreter()
        state = {"bonus": 1}

        @dicefunction(pure=True)
        def add_stateful_bonus(value):
            return value + state["bonus"]

        session.register_function(add_stateful_bonus)
        self.assertEqual(session("add_stateful_bonus(3)"), 4)
        state["bonus"] = 2
        self.assertEqual(session("add_stateful_bonus(3)"), 4)
        session.invalidate_caches()
        self.assertEqual(session("add_stateful_bonus(3)"), 5)

    def test_plain_expression_does_not_invalidate_caches(self):
        session = dice_interpreter()
        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: only_distribution(session("1 + 1")),
        )
        self.assertEqual(result[2], 1)
        self.assertEqual(invalidations, 0)

    def test_pure_dsl_function_call_does_not_invalidate_caches(self):
        session = dice_interpreter()
        session("double(value): value + value")
        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: only_distribution(session("double(3)")),
        )
        self.assertEqual(result[6], 1)
        self.assertEqual(invalidations, 0)

    def test_local_assignment_inside_function_does_not_invalidate_caches(self):
        session = dice_interpreter()
        session("rebind(value):\n    value = value + 1\n    value")
        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: only_distribution(session("rebind(3)")),
        )
        self.assertEqual(result[4], 1)
        self.assertEqual(invalidations, 0)

    def test_pure_registered_host_function_call_does_not_invalidate_caches(self):
        session = dice_interpreter()

        @dicefunction(pure=True)
        def add_bonus(value):
            return value + 1

        session.register_function(add_bonus)
        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: session("add_bonus(3)"),
        )
        self.assertEqual(result, 4)
        self.assertEqual(invalidations, 0)

    def test_repeated_dice_import_does_not_invalidate_caches_again(self):
        session = dice_interpreter()
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            helper = root / "helpers.dice"
            helper.write_text("add_one(value): value + 1\n", encoding="utf-8")

            session(f'import "{helper}"', current_dir=root)
            result, invalidations = self._count_invalidation_calls(
                session,
                lambda: session(f'import "{helper}"', current_dir=root),
            )
        self.assertIsNone(result)
        self.assertEqual(invalidations, 0)

    def test_global_assignment_invalidates_caches(self):
        session = dice_interpreter()
        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: session("bonus = 1"),
        )
        self.assertIsNone(result)
        self.assertEqual(invalidations, 1)

    def test_global_reassignment_invalidates_caches(self):
        session = dice_interpreter()
        session("bonus = 1")
        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: session("bonus = 2"),
        )
        self.assertIsNone(result)
        self.assertEqual(invalidations, 1)

    def test_function_definition_invalidates_caches(self):
        session = dice_interpreter()
        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: session("double(value): value + value"),
        )
        self.assertIsNone(result)
        self.assertEqual(invalidations, 1)

    def test_register_function_invalidates_caches(self):
        session = dice_interpreter()

        @dicefunction(pure=True)
        def add_bonus(value):
            return value + 1

        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: session.register_function(add_bonus),
        )
        self.assertIs(result, add_bonus)
        self.assertEqual(invalidations, 1)

    def test_session_assign_invalidates_caches(self):
        session = dice_interpreter()
        result, invalidations = self._count_invalidation_calls(
            session,
            lambda: session.assign("bonus", 3),
        )
        self.assertEqual(result, 3)
        self.assertEqual(invalidations, 1)

    def test_first_dice_import_invalidates_caches(self):
        session = dice_interpreter()
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            helper = root / "helpers.dice"
            helper.write_text("add_one(value): value + 1\n", encoding="utf-8")

            result, invalidations = self._count_invalidation_calls(
                session,
                lambda: session(f'import "{helper}"', current_dir=root),
            )
        self.assertIsNone(result)
        self.assertGreaterEqual(invalidations, 1)

    def test_first_python_import_invalidates_caches(self):
        session = dice_interpreter()
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            helper = root / "helpers.py"
            helper.write_text(
                "from dice import dicefunction\n\n"
                "@dicefunction(pure=True)\n"
                "def add_one(value):\n"
                "    return value + 1\n",
                encoding="utf-8",
            )

            result, invalidations = self._count_invalidation_calls(
                session,
                lambda: session(f'import "{helper}"', current_dir=root),
            )
        self.assertIsNone(result)
        self.assertGreaterEqual(invalidations, 1)

    def test_repeated_python_import_does_not_invalidate_caches_again(self):
        session = dice_interpreter()
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            helper = root / "helpers.py"
            helper.write_text(
                "from dice import dicefunction\n\n"
                "@dicefunction(pure=True)\n"
                "def add_one(value):\n"
                "    return value + 1\n",
                encoding="utf-8",
            )

            session(f'import "{helper}"', current_dir=root)
            result, invalidations = self._count_invalidation_calls(
                session,
                lambda: session(f'import "{helper}"', current_dir=root),
            )
        self.assertIsNone(result)
        self.assertEqual(invalidations, 0)


if __name__ == "__main__":
    unittest.main()
