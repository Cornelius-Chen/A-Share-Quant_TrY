from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v122y_cpo_baseline_vs_research_drawdown_compare_v1 import (
    V122YCpoBaselineVsResearchDrawdownCompareAnalyzer,
    write_report,
)


def test_v122y_cpo_baseline_vs_research_drawdown_compare(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports" / "analysis"
    reports_dir.mkdir(parents=True, exist_ok=True)
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)

    (reports_dir / "v122w_cpo_research_test_baseline_drawdown_attribution_v1.json").write_text(
        json.dumps({"drawdown_rows": [{"rank": 1, "peak_date": "2024-01-02", "trough_date": "2024-01-03", "drawdown": 0.1, "drawdown_amount": 100.0}]}),
        encoding="utf-8",
    )

    fieldnames = [
        "trade_date",
        "equity",
        "cash",
        "held_symbols",
        "position_count",
        "300308_qty",
        "300502_qty",
        "300757_qty",
        "688498_qty",
    ]
    with (training_dir / "cpo_baseline_daily_state_v1.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({"trade_date": "2024-01-02", "equity": "1000", "cash": "500", "held_symbols": "300308", "position_count": "1", "300308_qty": "100", "300502_qty": "0", "300757_qty": "0", "688498_qty": "0"})
        writer.writerow({"trade_date": "2024-01-03", "equity": "900", "cash": "500", "held_symbols": "300308", "position_count": "1", "300308_qty": "100", "300502_qty": "0", "300757_qty": "0", "688498_qty": "0"})
    with (training_dir / "cpo_research_test_baseline_daily_state_v1.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({"trade_date": "2024-01-02", "equity": "1200", "cash": "200", "held_symbols": "300308,300502", "position_count": "2", "300308_qty": "100", "300502_qty": "50", "300757_qty": "0", "688498_qty": "0"})
        writer.writerow({"trade_date": "2024-01-03", "equity": "1000", "cash": "200", "held_symbols": "300308,300502", "position_count": "2", "300308_qty": "100", "300502_qty": "50", "300757_qty": "0", "688498_qty": "0"})

    analyzer = V122YCpoBaselineVsResearchDrawdownCompareAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=reports_dir,
        report_name="v122y_cpo_baseline_vs_research_drawdown_compare_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["interval_count"] == 1
    assert result.interval_rows[0]["research_cash_ratio_peak"] < result.interval_rows[0]["baseline_cash_ratio_peak"]
