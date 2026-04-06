from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v122h_cpo_recent_1min_proxy_action_timepoint_label_base_v1 import (
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer,
    write_report,
)


def test_v122h_cpo_recent_1min_proxy_action_timepoint_label_base(tmp_path: Path) -> None:
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "symbol","bar_time","trade_date","clock_time","minute_index","is_late_session","open","high","low","close","volume","amount",
        "minute_return","range_pct","body_pct","upper_shadow_pct","lower_shadow_pct","close_location","close_vs_vwap","pullback_from_high",
        "push_efficiency","micro_pullback_depth","volume_ratio_5","value_ratio_5","prev_close_gap","reclaim_after_break_score",
        "burst_then_fade_score","late_session_integrity_score",
    ]
    path = training_dir / "cpo_recent_1min_microstructure_feature_table_v1.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for minute in range(10):
            close = 10 + minute * 0.1
            writer.writerow(
                {
                    "symbol": "300308",
                    "bar_time": f"2026-04-03 10:{minute:02d}:00",
                    "trade_date": "2026-04-03",
                    "clock_time": f"10:{minute:02d}:00",
                    "minute_index": minute,
                    "is_late_session": 0,
                    "open": close - 0.05,
                    "high": close + 0.08,
                    "low": close - 0.07,
                    "close": close,
                    "volume": 1000,
                    "amount": 10000,
                    "minute_return": 0.001,
                    "range_pct": 0.01,
                    "body_pct": 0.01,
                    "upper_shadow_pct": 0.001,
                    "lower_shadow_pct": 0.001,
                    "close_location": 0.8,
                    "close_vs_vwap": -0.001,
                    "pullback_from_high": -0.002,
                    "push_efficiency": 0.6,
                    "micro_pullback_depth": 0.001,
                    "volume_ratio_5": 1.0,
                    "value_ratio_5": 1.0,
                    "prev_close_gap": 0.001,
                    "reclaim_after_break_score": 0.001,
                    "burst_then_fade_score": 0.0001,
                    "late_session_integrity_score": 0.1,
                }
            )
    analyzer = V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122h_cpo_recent_1min_proxy_action_timepoint_label_base_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["row_count"] > 0
