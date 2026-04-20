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
    name: str
    expression: str
    setup_program: str | None = None
    description: str = ""
    modes: tuple[str, ...] = ("cold", "warm")

    def build(self) -> PreparedEvalInstance:
        return PreparedEvalInstance(
            setup_program=self.setup_program,
            expression=self.expression,
            source_name=f"<benchmark:{self.benchmark_id}>",
        )


CASES = (
    PreparedEvalCase(
        benchmark_id="scalar_add",
        name="Scalar Addition",
        expression="1 + 1",
        description="Minimal scalar arithmetic dispatch.",
    ),
    PreparedEvalCase(
        benchmark_id="distribution_add",
        name="Distribution Addition",
        expression="d20 + d8",
        description="Unswept exact distribution convolution.",
    ),
    PreparedEvalCase(
        benchmark_id="binary_roll",
        name="Binary Roll",
        expression="3 d 6",
        description="Exact NdS lowering through repeat_sum.",
    ),
    PreparedEvalCase(
        benchmark_id="keep_high",
        name="Keep High",
        expression="4 d 6 h 3",
        description="Roll-high operator over multiple dice.",
    ),
    PreparedEvalCase(
        benchmark_id="threshold_compare",
        name="Threshold Compare",
        expression="d20 >= 11",
        description="Boolean distribution comparison.",
    ),
    PreparedEvalCase(
        benchmark_id="branch_reselse",
        name="Branching Damage",
        expression="d20 >= 11 -> 8 | 0",
        description="Relative else branching over a Bernoulli guard.",
    ),
    PreparedEvalCase(
        benchmark_id="mean_summary",
        name="Mean Summary",
        expression="mean(d20 >= 11 -> 8 | 0)",
        description="Scalar summary over a distribution-valued branch.",
    ),
    PreparedEvalCase(
        benchmark_id="cum_summary",
        name="Cumulative Distribution",
        expression="cum(d20)",
        description="CDF helper over an unswept distribution.",
    ),
    PreparedEvalCase(
        benchmark_id="surv_summary",
        name="Survival Distribution",
        expression="surv(d20)",
        description="Survival helper over an unswept distribution.",
    ),
    PreparedEvalCase(
        benchmark_id="repeat_sum",
        name="Repeat Sum",
        expression="repeat_sum(8, d6)",
        description="Repeated addition through cached repeated squaring.",
    ),
    PreparedEvalCase(
        benchmark_id="dsl_scalar_call",
        name="Pure DSL Scalar Call",
        setup_program="double(value): value + value",
        expression="double(21)",
        description="Pure DSL call on a scalar argument.",
    ),
    PreparedEvalCase(
        benchmark_id="dsl_distribution_call",
        name="Pure DSL Distribution Call",
        setup_program="double(value): value + value",
        expression="double(d20)",
        description="Pure DSL call on a distribution argument.",
    ),
    PreparedEvalCase(
        benchmark_id="attack_vs_ac_sweep",
        name="Attack vs AC Sweep",
        setup_program="""
attack_damage(ac):
    d20 + 7 >= ac -> 8 | 0
""".strip(),
        expression="attack_damage([AC:10..25])",
        description="One-axis sweep over a cached pure DSL attack helper.",
    ),
    PreparedEvalCase(
        benchmark_id="damage_vs_ac_sweep",
        name="Damage vs AC Sweep",
        setup_program="""
damage(ac):
    repeat_sum(4, d6 + (d20 + 7 >= ac -> 3 | 0))
""".strip(),
        expression="damage([AC:10..28])",
        description="Medium cached sweep over a pure DSL helper with repeat_sum.",
    ),
    PreparedEvalCase(
        benchmark_id="two_axis_damage_sweep",
        name="Two-Axis Damage Sweep",
        setup_program="""
damage(ac, bless):
    hit_bonus = bless == 1 -> d4 | 0
    repeat_sum(4, d6 + (d20 + 7 + hit_bonus >= ac -> 3 | 0))
""".strip(),
        expression="damage([AC:10..26], [BLESS:0, 1])",
        description="Two-axis pure sweep intended to show cache-sensitive reuse.",
    ),
)
