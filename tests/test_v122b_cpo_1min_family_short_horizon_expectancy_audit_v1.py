from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v122b_cpo_1min_family_short_horizon_expectancy_audit_v1 import (
    V122BCpo1MinFamilyShortHorizonExpectancyAuditAnalyzer,
    write_report,
)


def test_v122b_cpo_1min_family_short_horizon_expectancy_audit(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports" / "analysis"
    reports_dir.mkdir(parents=True, exist_ok=True)
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)

    (reports_dir / "v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1.json").write_text(
        json.dumps({"summary": {"candidate_band_names": ["pc1_low__pc2_low"]}}),
        encoding="utf-8",
    )
    (reports_dir / "v121z_cpo_recent_1min_burst_fade_trap_candidate_discovery_v1.json").write_text(
        json.dumps({"summary": {"candidate_band_names": ["pc1_high__pc2_high"]}}),
        encoding="utf-8",
    )

    fieldnames = [
        "symbol",
        "bar_time",
        "trade_date",
        "clock_time",
        "minute_index",
        "is_late_session",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "minute_return",
        "range_pct",
        "body_pct",
        "upper_shadow_pct",
        "lower_shadow_pct",
        "close_location",
        "close_vs_vwap",
        "pullback_from_high",
        "push_efficiency",
        "micro_pullback_depth",
        "volume_ratio_5",
        "value_ratio_5",
        "prev_close_gap",
        "reclaim_after_break_score",
        "burst_then_fade_score",
        "late_session_integrity_score",
    ]
    table_path = training_dir / "cpo_recent_1min_microstructure_feature_table_v1.csv"
    with table_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index in range(12):
            writer.writerow(
                {
                    "symbol": "300308",
                    "bar_time": f"2026-04-03 10:{index:02d}:00",
                    "trade_date": "2026-04-03",
                    "clock_time": f"10:{index:02d}:00",
                    "minute_index": index,
                    "is_late_session": 0,
                    "open": 10 + index * 0.1,
                    "high": 10.2 + index * 0.1,
                    "low": 9.9 + index * 0.1,
                    "close": 10.1 + index * 0.1,
                    "volume": 1000 + index * 10,
                    "amount": 10000 + index * 100,
                    "minute_return": 0.001 * index,
                    "range_pct": 0.02 + 0.001 * index,
                    "body_pct": 0.01 + 0.0005 * index,
                    "upper_shadow_pct": 0.001 * index,
                    "lower_shadow_pct": 0.001 * index,
                    "close_location": 0.45 + 0.01 * index,
                    "close_vs_vwap": -0.001 * index,
                    "pullback_from_high": -0.02 + 0.001 * index,
                    "push_efficiency": 0.1 if index < 6 else -0.8,
                    "micro_pullback_depth": 0.001 * index,
                    "volume_ratio_5": 1.0 + 0.1 * index,
                    "value_ratio_5": 1.0 + 0.11 * index,
                    "prev_close_gap": 0.0005 * index,
                    "reclaim_after_break_score": 0.0007 * index,
                    "burst_then_fade_score": 0.0002 * index,
                    "late_session_integrity_score": 0.1 if index < 6 else -0.2,
                }
            )

    analyzer = V122BCpo1MinFamilyShortHorizonExpectancyAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=reports_dir,
        report_name="v122b_cpo_1min_family_short_horizon_expectancy_audit_v1",
        result=result,
    )
    assert output_path.exists()
    assert result.summary["horizon_bars"] == 5
