from __future__ import annotations

import csv
from pathlib import Path

from a_share_quant.strategy.v122i_cpo_1min_proxy_label_base_readiness_audit_v1 import (
    V122ICpo1MinProxyLabelBaseReadinessAuditAnalyzer,
    write_report,
)


def test_v122i_cpo_1min_proxy_label_base_readiness_audit(tmp_path: Path) -> None:
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)
    path = training_dir / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "symbol","trade_date","bar_time","clock_time","proxy_action_label","forward_return_5","max_favorable_return_5",
                "max_adverse_return_5","push_efficiency","close_vs_vwap","close_location","late_session_integrity_score",
                "burst_then_fade_score","reclaim_after_break_score",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "symbol": "300308",
                "trade_date": "2026-04-03",
                "bar_time": "2026-04-03 10:00:00",
                "clock_time": "10:00:00",
                "proxy_action_label": "add_probe",
                "forward_return_5": "0.01",
                "max_favorable_return_5": "0.02",
                "max_adverse_return_5": "-0.001",
                "push_efficiency": "0.5",
                "close_vs_vwap": "0.0",
                "close_location": "0.8",
                "late_session_integrity_score": "0.1",
                "burst_then_fade_score": "0.0",
                "reclaim_after_break_score": "0.01",
            }
        )
    analyzer = V122ICpo1MinProxyLabelBaseReadinessAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122i_cpo_1min_proxy_label_base_readiness_audit_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["symbol_count"] == 1
