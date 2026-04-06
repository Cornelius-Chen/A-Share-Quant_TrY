from pathlib import Path

from a_share_quant.strategy.v123l_cpo_heat_guardrail_drawdown_interval_compare_v1 import (
    V123LCpoHeatGuardrailDrawdownIntervalCompareAnalyzer,
)


def test_v123l_heat_guardrails_improve_uncapped_drawdowns() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123LCpoHeatGuardrailDrawdownIntervalCompareAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["interval_count"] == 3
    improvements = [row["balanced_heat_guardrail_drawdown_improvement"] for row in result.interval_rows]
    strict_improvements = [row["strict_heat_guardrail_drawdown_improvement"] for row in result.interval_rows]
    assert max(improvements) > 0.0
    assert max(strict_improvements) > 0.0
    assert result.interval_rows[2]["balanced_heat_guardrail_drawdown_improvement"] == 0.0
    assert result.interval_rows[2]["strict_heat_guardrail_drawdown_improvement"] == 0.0
