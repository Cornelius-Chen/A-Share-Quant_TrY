from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v122j_cpo_1min_supportive_family_proxy_label_audit_v1 import (
    V122JCpo1MinSupportiveFamilyProxyLabelAuditAnalyzer,
    write_report,
)
from tests.test_v122e_cpo_1min_supportive_quality_discovery_v1 import _write_minimal_supportive_fixture


def test_v122j_cpo_1min_supportive_family_proxy_label_audit(tmp_path: Path) -> None:
    _write_minimal_supportive_fixture(tmp_path)
    training_dir = tmp_path / "data" / "training"
    label_path = training_dir / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv"
    with label_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "symbol","trade_date","bar_time","clock_time","proxy_action_label","forward_return_5","max_favorable_return_5",
                "max_adverse_return_5","push_efficiency","close_vs_vwap","close_location","late_session_integrity_score",
                "burst_then_fade_score","reclaim_after_break_score",
            ],
        )
        writer.writeheader()
        for symbol in ["300308", "300502"]:
            for date in ["2026-04-01", "2026-04-02"]:
                for minute in range(3):
                    writer.writerow(
                        {
                            "symbol": symbol,
                            "trade_date": date,
                            "bar_time": f"{date} 10:0{minute}:00",
                            "clock_time": f"10:0{minute}:00",
                            "proxy_action_label": "add_probe" if minute < 2 else "hold_probe",
                            "forward_return_5": "0.01",
                            "max_favorable_return_5": "0.02",
                            "max_adverse_return_5": "-0.001",
                            "push_efficiency": "0.6",
                            "close_vs_vwap": "-0.001",
                            "close_location": "0.8",
                            "late_session_integrity_score": "0.2",
                            "burst_then_fade_score": "0.0001",
                            "reclaim_after_break_score": "0.001",
                        }
                    )

    analyzer = V122JCpo1MinSupportiveFamilyProxyLabelAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122j_cpo_1min_supportive_family_proxy_label_audit_v1",
        result=result,
    )
    assert output_path.exists()
    assert result.summary["base_row_count"] > 0
