from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114z_cpo_intraday_key_window_availability_audit_v1 import (
    V114ZCpoIntradayKeyWindowAvailabilityAuditAnalyzer,
    load_json_report,
)


def test_v114z_cpo_intraday_key_window_availability_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114ZCpoIntradayKeyWindowAvailabilityAuditAnalyzer(repo_root=repo_root)

    def fake_fetch(symbol: str, trade_date: str) -> dict[str, object]:
        return {
            "row_count": 240 if symbol in {"300308", "300502"} else 0,
            "columns": ["时间", "开盘", "收盘", "最高", "最低", "成交量", "成交额"],
            "nonempty": symbol in {"300308", "300502"},
        }

    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports/analysis/v113n_cpo_real_board_episode_population_v1.json"),
        fetch_intraday=fake_fetch,
    )

    assert result.summary["focus_symbol_count"] == 4
    assert result.summary["key_window_count"] == 19
    assert result.summary["success_nonempty_count"] > 0
    assert result.summary["historical_intraday_provider_ready_now"] is False
    assert any(row["fetch_status"] == "success_empty" for row in result.availability_rows)
