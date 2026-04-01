from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v115a_cpo_baostock_midfreq_intraday_audit_v1 import (
    V115ACpoBaostockMidfreqIntradayAuditAnalyzer,
    load_json_report,
)


def test_v115a_cpo_baostock_midfreq_intraday_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115ACpoBaostockMidfreqIntradayAuditAnalyzer(repo_root=repo_root)

    def fake_fetch(symbol: str, trade_date: str, frequency: str) -> dict[str, object]:
        nonempty = frequency in {"5", "15"}
        return {
            "row_count": 48 if nonempty else 0,
            "nonempty": nonempty,
            "sample_head": [["2025-07-24", "20250724093500000"]],
            "sample_tail": [["2025-07-24", "20250724150000000"]] if nonempty else [],
        }

    result = analyzer.analyze(
        v114z_payload=load_json_report(repo_root / "reports/analysis/v114z_cpo_intraday_key_window_availability_audit_v1.json"),
        fetch_baostock=fake_fetch,
    )

    assert result.summary["manifest_window_count"] == 19
    assert result.summary["attempt_count"] == 76
    assert result.summary["success_nonempty_count"] > 0
    assert result.summary["midfreq_historical_intraday_partially_ready"] is True
    assert result.summary["midfreq_historical_intraday_fully_ready"] is False
