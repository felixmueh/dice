from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dice import dice_interpreter
from diceparser import DiceParser
from lexer import Lexer


ROOT = Path(__file__).resolve().parents[2]


def _parse_statement(text: str, source_name: str):
    parser = DiceParser(Lexer(text, source_name=source_name))
    return parser.parse() if (";" in text or "\n" in text) else parser.statement()


class PreparedEvalInstance:
    def __init__(self, setup_program: str | None, expression: str, source_name: str):
        self.session = dice_interpreter(current_dir=str(ROOT))
        if setup_program:
            self.session(setup_program, current_dir=str(ROOT))
        self.ast = _parse_statement(expression, source_name=source_name)

    def run_once(self):
        interpreter = self.session.interpreter
        interpreter.ast = self.ast
        interpreter.warnings = []
        return interpreter.interpret()

    def reset(self):
        self.session.invalidate_caches()


@dataclass(frozen=True)
class PreparedEvalCase:
    benchmark_id: str
    expression: str
    setup_program: str | None = None
    description: str = ""

    def build(self) -> PreparedEvalInstance:
        return PreparedEvalInstance(
            setup_program=self.setup_program,
            expression=self.expression,
            source_name=f"<benchmark:{self.benchmark_id}>",
        )


CASES = (
    PreparedEvalCase("scalar_add", "1 + 1", description="Minimal scalar arithmetic dispatch."),
    PreparedEvalCase("scalar_sub", "17 - 9", description="Scalar subtraction dispatch."),
    PreparedEvalCase("scalar_mul", "6 * 7", description="Scalar multiplication dispatch."),
    PreparedEvalCase("scalar_div", "21 / 3", description="Scalar division dispatch."),
    PreparedEvalCase("scalar_floordiv", "21 // 4", description="Scalar floor division dispatch."),
    PreparedEvalCase("scalar_neg", "-(d6)", description="Unary negation over a distribution."),
    PreparedEvalCase("distribution_add", "d20 + d8", description="Unswept exact distribution convolution."),
    PreparedEvalCase("distribution_compare", "d20 >= d12", description="Distribution-vs-distribution comparison."),
    PreparedEvalCase("membership", "d20 in {1, 20}", description="Non-contiguous event membership query."),
    PreparedEvalCase("binary_roll", "3 d 6", description="Exact NdS lowering through repeat_sum."),
    PreparedEvalCase("keep_high", "4 d 6 h 3", description="Roll-high operator over multiple dice."),
    PreparedEvalCase("keep_low", "4 d 6 l 3", description="Roll-low operator over multiple dice."),
    PreparedEvalCase("branch_reselse", "d20 >= 11 -> 8 | 0", description="Relative else branching over a Bernoulli guard."),
    PreparedEvalCase("mean_summary", "mean(d20 >= 11 -> 8 | 0)", description="Mean over a distribution-valued branch."),
    PreparedEvalCase("var_summary", "var(d20 + d8)", description="Variance summary over a distribution."),
    PreparedEvalCase("std_summary", "std(d20 + d8)", description="Standard deviation summary over a distribution."),
    PreparedEvalCase("cum_summary", "cum(d20)", description="CDF helper over an unswept distribution."),
    PreparedEvalCase("surv_summary", "surv(d20)", description="Survival helper over an unswept distribution."),
    PreparedEvalCase("repeat_sum", "repeat_sum(8, d6)", description="Repeated addition through repeated squaring."),
    PreparedEvalCase("sweep_arithmetic", "[AC:10..25] + 7", description="One-axis scalar sweep arithmetic."),
    PreparedEvalCase("sweep_compare", "d20 >= [AC:10..25]", description="Distribution against a named scalar sweep."),
    PreparedEvalCase("sweep_reorder_index", '([PLAN:1, 2] + [AC:10, 11])["AC", "PLAN"]', description="Axis reordering index operation."),
    PreparedEvalCase("sweep_coordinate_index", "([PLAN:1, 2] + [AC:10, 11])[PLAN: 2]", description="Coordinate indexing on a named axis."),
    PreparedEvalCase("sweep_filter_index", "([PLAN:1, 2] + [AC:10, 11, 12])[AC in {10, 12}]", description="Axis filter indexing."),
    PreparedEvalCase("sweep_positional_index", '([PLAN:1, 2] + [AC:10, 11])[1, 0]', description="Positional coordinate indexing."),
    PreparedEvalCase("sumover_named_axis", 'sumover([PLAN:1, 2] + [AC:10, 11], "PLAN")', description="Reducer over one named sweep axis."),
    PreparedEvalCase("meanover_named_axis", 'meanover(d2 + [bonus:0, 1], "bonus")', description="Mean reducer over a named axis."),
    PreparedEvalCase("maxover_named_axis", 'maxover([PLAN:1, 2] + [AC:10, 11], "PLAN")', description="Max reducer over a named axis."),
    PreparedEvalCase("argmaxover_named_axis", 'argmaxover([PLAN:1, 2] + [AC:10, 11], "PLAN")', description="Argmax reducer over a named axis."),
    PreparedEvalCase("sumover_multi_axis", 'sumover([PLAN:1, 2] + [LEVEL:10, 20] + [AC:100, 200], ("PLAN", "LEVEL"))', description="Reducer over multiple named axes."),
    PreparedEvalCase("meanover_multi_axis", 'meanover([PLAN:1, 2] + [LEVEL:10, 20], ("PLAN", "LEVEL"))', description="Mean reducer over multiple named axes."),
    PreparedEvalCase("attack_vs_ac_sweep", "repeat_sum(2, d20 >= [AC:10..25] -> 1 | 0)", description="Sweep-heavy attack tally."),
    PreparedEvalCase("damage_vs_ac_sweep", "repeat_sum(4, d6 + (d20 + 7 >= [AC:10..28] -> 3 | 0))", description="One-axis damage sweep with repeat_sum."),
    PreparedEvalCase("two_axis_damage_sweep", "repeat_sum(4, d6 + (d20 + 7 + ([BLESS:0, 1] == 1 -> d4 | 0) >= [AC:10..26] -> 3 | 0))", description="Two-axis damage sweep with inline bless logic."),
)
