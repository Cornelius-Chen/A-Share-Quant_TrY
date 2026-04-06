from pathlib import Path

from a_share_quant.strategy.v131m_commercial_aerospace_5min_feasibility_audit_v1 import (
    V131MCommercialAerospace5MinFeasibilityAuditAnalyzer,
)


def test_v131m_commercial_aerospace_5min_feasibility_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    def fake_fetch(symbol: str, trade_date: str) -> dict[str, object]:
        if symbol in {"300342", "601698"}:
            return {"row_count": 48, "nonempty": True, "sample_head": [["a"]], "sample_tail": [["b"]]}
        return {"row_count": 0, "nonempty": False, "sample_head": [], "sample_tail": []}

    result = V131MCommercialAerospace5MinFeasibilityAuditAnalyzer(repo_root).analyze(
        fetch_baostock_5min=fake_fetch
    )

    assert result.summary["manifest_row_count"] == 4
    assert result.summary["success_nonempty_count"] == 2
    assert result.summary["five_min_partially_ready"] is True
    assert result.summary["five_min_fully_ready"] is False
