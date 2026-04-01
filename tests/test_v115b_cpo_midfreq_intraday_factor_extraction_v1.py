from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v115b_cpo_midfreq_intraday_factor_extraction_v1 import (
    V115BCpoMidfreqIntradayFactorExtractionAnalyzer,
    load_json_report,
)


def test_v115b_cpo_midfreq_intraday_factor_extraction() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115BCpoMidfreqIntradayFactorExtractionAnalyzer(repo_root=repo_root)

    def fake_fetch(symbol: str, trade_date: str, frequency: str) -> list[dict[str, float | str]]:
        if symbol == "300308" and trade_date == "2024-03-15":
            closes = [10.0, 9.8, 9.6, 9.4]
            highs = [10.2, 10.1, 10.0, 9.9]
            lows = [9.9, 9.7, 9.5, 9.3]
        else:
            closes = [10.0, 10.3, 10.5, 10.8]
            highs = [10.1, 10.4, 10.6, 10.9]
            lows = [9.9, 10.0, 10.2, 10.4]
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
        v114z_payload=load_json_report(repo_root / "reports/analysis/v114z_cpo_intraday_key_window_availability_audit_v1.json"),
        fetch_window_rows=fake_fetch,
    )

    assert result.summary["window_count"] == 19
    assert result.summary["failed_window_count"] == 0
    assert result.summary["risk_window_count"] > 0
    assert result.summary["top_separating_factor"] is not None
    assert any(abs(float(row["mean_gap"])) > 0 for row in result.separation_rows)
