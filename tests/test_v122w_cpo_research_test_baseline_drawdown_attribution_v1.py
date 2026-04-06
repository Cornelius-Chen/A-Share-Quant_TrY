from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v122w_cpo_research_test_baseline_drawdown_attribution_v1 import (
    V122WCpoResearchTestBaselineDrawdownAttributionAnalyzer,
    write_report,
)


def test_v122w_cpo_research_test_baseline_drawdown_attribution(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports" / "analysis"
    reports_dir.mkdir(parents=True, exist_ok=True)
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = tmp_path / "data" / "raw" / "daily_bars"
    raw_dir.mkdir(parents=True, exist_ok=True)

    (reports_dir / "v120k_cpo_research_test_baseline_top_drawdown_dashboard_v1.json").write_text(
        json.dumps(
            {
                "top_drawdown_rows": [
                    {
                        "rank": 1,
                        "peak_date": "2024-01-02",
                        "trough_date": "2024-01-03",
                        "drawdown": 0.1,
                        "drawdown_amount": 100000.0,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with (training_dir / "cpo_research_test_baseline_daily_state_v1.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "trade_date",
                "equity",
                "cash",
                "held_symbols",
                "position_count",
                "300308_qty",
                "300502_qty",
                "300757_qty",
                "688498_qty",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "trade_date": "2024-01-02",
                "equity": "1000000",
                "cash": "100000",
                "held_symbols": "300308,300502",
                "position_count": "2",
                "300308_qty": "100",
                "300502_qty": "200",
                "300757_qty": "0",
                "688498_qty": "0",
            }
        )
        writer.writerow(
            {
                "trade_date": "2024-01-03",
                "equity": "900000",
                "cash": "120000",
                "held_symbols": "300308,300502",
                "position_count": "2",
                "300308_qty": "100",
                "300502_qty": "200",
                "300757_qty": "0",
                "688498_qty": "0",
            }
        )

    with (training_dir / "cpo_research_test_baseline_trade_explainer_v1.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "lane",
                "execution_trade_date",
                "symbol",
                "action",
                "reason",
                "weight_vs_initial_capital",
                "notional",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "lane": "research_test_baseline",
                "execution_trade_date": "2024-01-03",
                "symbol": "300308",
                "action": "add",
                "reason": "test_reason",
                "weight_vs_initial_capital": "0.05",
                "notional": "50000",
            }
        )

    with (raw_dir / "sina_daily_bars_cpo_execution_main_feed_v1.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=["trade_date", "symbol", "close"])
        writer.writeheader()
        writer.writerow({"trade_date": "2024-01-02", "symbol": "300308", "close": "10"})
        writer.writerow({"trade_date": "2024-01-03", "symbol": "300308", "close": "9"})
        writer.writerow({"trade_date": "2024-01-02", "symbol": "300502", "close": "20"})
        writer.writerow({"trade_date": "2024-01-03", "symbol": "300502", "close": "19"})

    analyzer = V122WCpoResearchTestBaselineDrawdownAttributionAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=reports_dir,
        report_name="v122w_cpo_research_test_baseline_drawdown_attribution_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["drawdown_count"] == 1
    assert result.drawdown_rows[0]["interval_trade_count"] == 1
