from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v122x_cpo_baseline_daily_state_rebuild_v1 import (
    V122XCpoBaselineDailyStateRebuildAnalyzer,
    write_daily_state_csv,
    write_report,
)


def test_v122x_cpo_baseline_daily_state_rebuild(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports" / "analysis"
    reports_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = tmp_path / "data" / "raw" / "daily_bars"
    raw_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "replay_day_rows": [
            {"trade_date": "2024-01-02", "equity_after_close": 1000.0, "cash_after_close": 900.0},
            {"trade_date": "2024-01-03", "equity_after_close": 1100.0, "cash_after_close": 800.0},
        ],
        "executed_order_rows": [
            {"execution_trade_date": "2024-01-03", "symbol": "300308", "action": "buy", "quantity": 100}
        ],
    }
    (reports_dir / "v114t_cpo_replay_integrity_repair_v1.json").write_text(json.dumps(payload), encoding="utf-8")
    with (raw_dir / "sina_daily_bars_cpo_execution_main_feed_v1.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["trade_date", "symbol", "close"])
        writer.writeheader()
        writer.writerow({"trade_date": "2024-01-03", "symbol": "300308", "close": "10"})

    analyzer = V122XCpoBaselineDailyStateRebuildAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    report = write_report(
        reports_dir=reports_dir,
        report_name="v122x_cpo_baseline_daily_state_rebuild_v1",
        result=result,
    )
    csv_out = write_daily_state_csv(
        output_path=tmp_path / "data" / "training" / "cpo_baseline_daily_state_v1.csv",
        rows=result.daily_state_rows,
    )
    assert report.exists()
    assert csv_out.exists()
    assert result.daily_state_rows[-1]["300308_qty"] == 100
