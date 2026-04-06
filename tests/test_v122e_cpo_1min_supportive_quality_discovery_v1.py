from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v122e_cpo_1min_supportive_quality_discovery_v1 import (
    V122ECpo1MinSupportiveQualityDiscoveryAnalyzer,
    write_report,
)


def _write_minimal_supportive_fixture(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports" / "analysis"
    reports_dir.mkdir(parents=True, exist_ok=True)
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1.json").write_text(
        json.dumps({"summary": {"candidate_band_names": ["pc1_low__pc2_low"]}}),
        encoding="utf-8",
    )
    fieldnames = [
        "symbol","bar_time","trade_date","clock_time","minute_index","is_late_session","open","high","low","close","volume","amount",
        "minute_return","range_pct","body_pct","upper_shadow_pct","lower_shadow_pct","close_location","close_vs_vwap","pullback_from_high",
        "push_efficiency","micro_pullback_depth","volume_ratio_5","value_ratio_5","prev_close_gap","reclaim_after_break_score",
        "burst_then_fade_score","late_session_integrity_score",
    ]
    table_path = training_dir / "cpo_recent_1min_microstructure_feature_table_v1.csv"
    with table_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for symbol in ["300308", "300502"]:
            for date_index, trade_date in enumerate(["2026-04-01", "2026-04-02"]):
                for minute in range(8):
                    close = 10 + date_index + minute * 0.1
                    writer.writerow(
                        {
                            "symbol": symbol,
                            "bar_time": f"{trade_date} 10:{minute:02d}:00",
                            "trade_date": trade_date,
                            "clock_time": f"10:{minute:02d}:00",
                            "minute_index": minute,
                            "is_late_session": 0,
                            "open": close - 0.05,
                            "high": close + 0.05,
                            "low": close - 0.08,
                            "close": close,
                            "volume": 1000,
                            "amount": 10000,
                            "minute_return": 0.001 * minute,
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
                            "late_session_integrity_score": 0.2,
                        }
                    )


def test_v122e_cpo_1min_supportive_quality_discovery(tmp_path: Path) -> None:
    _write_minimal_supportive_fixture(tmp_path)
    analyzer = V122ECpo1MinSupportiveQualityDiscoveryAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122e_cpo_1min_supportive_quality_discovery_v1",
        result=result,
    )
    assert output_path.exists()
    assert result.summary["sample_count"] > 0
