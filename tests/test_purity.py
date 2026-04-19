import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

os.environ.setdefault("MPLBACKEND", "Agg")
mpl_config = Path(tempfile.gettempdir()) / "dice-mplconfig"
mpl_config.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(mpl_config))

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dice import dice_interpreter, dicefunction
from lexer import (
    ADV,
    ASSIGN,
    AVG,
    CARET,
    DIS,
    DIV,
    ELSE,
    EQUAL,
    FLOORDIV,
    GREATER,
    GREATER_OR_EQUAL,
    HIGH,
    IN,
    LESS,
    LESS_OR_EQUAL,
    LOW,
    MINUS,
    MUL,
    PLUS,
    PRINT,
    PROP,
    RES,
    ROLL,
)
from purity import BINARY_OPERATOR_PURITY, TENARY_OPERATOR_PURITY, UNARY_OPERATOR_PURITY

DISPATCHED_UNARY_OPERATORS = frozenset((ROLL, ADV, DIS, AVG, PROP, MINUS, PRINT))
DISPATCHED_BINARY_OPERATORS = frozenset(
    (
        PLUS,
        MINUS,
        MUL,
        CARET,
        DIV,
        FLOORDIV,
        ROLL,
        GREATER_OR_EQUAL,
        LESS_OR_EQUAL,
        GREATER,
        LESS,
        EQUAL,
        IN,
        RES,
        ASSIGN,
    )
)
DISPATCHED_TENARY_OPERATORS = frozenset(((RES, ELSE), (ROLL, HIGH), (ROLL, LOW)))


class PurityTest(unittest.TestCase):
    def test_operator_metadata_covers_interpreter_dispatch(self):
        self.assertEqual(set(UNARY_OPERATOR_PURITY), DISPATCHED_UNARY_OPERATORS)
        self.assertEqual(set(BINARY_OPERATOR_PURITY), DISPATCHED_BINARY_OPERATORS)
        self.assertEqual(set(TENARY_OPERATOR_PURITY), DISPATCHED_TENARY_OPERATORS)

    def test_purity_analyzer_marks_pure_and_impure_functions(self):
        session = dice_interpreter()

        @dicefunction(pure=True)
        def add_bonus(value):
            return value + 1

        @dicefunction
        def log_value(value):
            return value + 1

        session.register_function(add_bonus)
        session.register_function(log_value)
        session("pure_wrap(value): add_bonus(value)")
        session("impure_wrap(value): log_value(value)")
        session("samples(): !d6")

        self.assertTrue(session.interpreter.purity_analyzer.function_is_pure(session.interpreter.callable_scope["pure_wrap"]))
        self.assertFalse(session.interpreter.purity_analyzer.function_is_pure(session.interpreter.callable_scope["impure_wrap"]))
        self.assertFalse(session.interpreter.purity_analyzer.function_is_pure(session.interpreter.callable_scope["samples"]))

    def test_mutual_recursion_is_rejected_during_purity_analysis(self):
        session = dice_interpreter()
        session("left(value): right(value)\nright(value): left(value)")
        with self.assertRaisesRegex(Exception, "recursive purity dependency detected"):
            session("left(3)")


if __name__ == "__main__":
    unittest.main()
