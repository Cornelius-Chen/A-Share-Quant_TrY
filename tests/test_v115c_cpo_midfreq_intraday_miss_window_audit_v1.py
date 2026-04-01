from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v115c_cpo_midfreq_intraday_miss_window_audit_v1 import (
    V115CCpoMidfreqIntradayMissWindowAuditAnalyzer,
    load_json_report,
)


def test_v115c_cpo_midfreq_intraday_miss_window_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115CCpoMidfreqIntradayMissWindowAuditAnalyzer(repo_root=repo_root)

    def fake_fetch(symbol: str, trade_date: str, frequency: str) -> list[dict[str, float | str]]:
        strong_pair = {("300502", "2023-05-18"), ("300308", "2024-02-06")}
        if (symbol, trade_date) in strong_pair:
            closes = [10.0, 10.3, 10.5, 10.8]
            highs = [10.1, 10.4, 10.6, 10.9]
            lows = [9.9, 10.0, 10.2, 10.4]
        else:
            closes = [10.0, 9.9, 9.8, 9.7]
            highs = [10.0, 10.0, 9.95, 9.9]
            lows = [9.9, 9.8, 9.7, 9.6]
        rows = []
        for idx, close in enumerate(closes):
            rows.append(
                {
                    "date": trade_date,
                    "time": f"{trade_date.replace('-', '')}093{idx}00000",
                    "code": symbol,
                    "open": 10.0 if idx == 0 else closes[idx - 1],
                    "high": highs[idx],
                    "low": lows[idx],
                    "close": close,
                    "volume": 1000.0 + idx * 100,
                    "amount": (1000.0 + idx * 100) * close,
                    "adjustflag": "2",
                }
            )
        return rows

    result = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
        v114w_payload=load_json_report(repo_root / "reports/analysis/v114w_cpo_under_exposure_attribution_repaired_v1.json"),
        v115b_payload=load_json_report(repo_root / "reports/analysis/v115b_cpo_midfreq_intraday_factor_extraction_v1.json"),
        fetch_window_rows=fake_fetch,
    )

    assert result.summary["miss_day_count"] == 6
    assert result.summary["successful_miss_window_count"] > 0
    assert result.summary["candidate_add_confirmation_count"] > 0
    assert any(bool(row.get("f30_candidate_add_confirmation")) or bool(row.get("f60_candidate_add_confirmation")) for row in result.candidate_add_confirmation_rows)
