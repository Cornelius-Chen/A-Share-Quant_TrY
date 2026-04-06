from __future__ import annotations

import csv
from pathlib import Path

from a_share_quant.strategy.v122s_cpo_1min_historical_bridge_overlap_audit_v1 import (
    V122SCpo1MinHistoricalBridgeOverlapAuditAnalyzer,
    write_report,
)


def test_v122s_cpo_1min_historical_bridge_overlap_audit(tmp_path: Path) -> None:
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)
    with (training_dir / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=["signal_trade_date", "action_context"])
        writer.writeheader()
        writer.writerow({"signal_trade_date": "2026-01-06", "action_context": "reduce_vs_hold"})
        writer.writerow({"signal_trade_date": "2025-12-31", "action_context": "reduce_vs_hold"})
    with (training_dir / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=["trade_date", "symbol", "clock_time"])
        writer.writeheader()
        writer.writerow({"trade_date": "2026-03-24", "symbol": "300308", "clock_time": "10:00:00"})
        writer.writerow({"trade_date": "2026-03-25", "symbol": "300502", "clock_time": "10:01:00"})

    analyzer = V122SCpo1MinHistoricalBridgeOverlapAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122s_cpo_1min_historical_bridge_overlap_audit_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["overlap_day_count"] == 0
