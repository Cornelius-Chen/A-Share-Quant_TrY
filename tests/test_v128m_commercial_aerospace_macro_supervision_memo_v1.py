from pathlib import Path

from a_share_quant.strategy.v128m_commercial_aerospace_macro_supervision_memo_v1 import (
    V128MCommercialAerospaceMacroSupervisionMemoAnalyzer,
)


def test_v128m_commercial_aerospace_macro_supervision_memo_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128MCommercialAerospaceMacroSupervisionMemoAnalyzer(repo_root).analyze()

    assert result.summary["current_primary_variant"] == "tail_weakdrift_full"
    assert round(float(result.summary["current_primary_final_equity"]), 4) == 1309426.5555
    assert round(float(result.summary["current_primary_max_drawdown"]), 8) == 0.09309927
    assert len(result.priority_rows) >= 5
    assert any(row["theme"] == "pre_open_decisive_event_veto" for row in result.priority_rows)
