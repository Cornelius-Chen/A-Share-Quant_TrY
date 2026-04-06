from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v121x_cpo_recent_1min_pca_structure_audit_v1 import (
    V121XCpoRecent1MinPcaStructureAuditAnalyzer,
    write_report,
)


def test_v121x_cpo_recent_1min_pca_structure_audit(tmp_path: Path) -> None:
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)
    table_path = training_dir / "cpo_recent_1min_microstructure_feature_table_v1.csv"
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
    with table_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index in range(6):
            writer.writerow(
                {
                    "symbol": "300308",
                    "bar_time": f"2026-04-03 10:3{index}:00",
                    "trade_date": "2026-04-03",
                    "clock_time": f"10:3{index}:00",
                    "minute_index": index,
                    "is_late_session": 0,
                    "open": 10.0 + index * 0.1,
                    "high": 10.2 + index * 0.1,
                    "low": 9.9 + index * 0.1,
                    "close": 10.1 + index * 0.05,
                    "volume": 1000 + index * 100,
                    "amount": 10000 + index * 1200,
                    "minute_return": 0.001 * index,
                    "range_pct": 0.02 + 0.001 * index,
                    "body_pct": 0.01 + 0.0005 * index,
                    "upper_shadow_pct": 0.003 * index,
                    "lower_shadow_pct": 0.002 * index,
                    "close_location": 0.4 + 0.05 * index,
                    "close_vs_vwap": -0.002 + 0.001 * index,
                    "pullback_from_high": -0.01 + 0.001 * index,
                    "push_efficiency": 0.2 + 0.05 * index,
                    "micro_pullback_depth": 0.005 * index,
                    "volume_ratio_5": 1.0 + 0.1 * index,
                    "value_ratio_5": 1.0 + 0.12 * index,
                    "prev_close_gap": -0.001 + 0.0008 * index,
                    "reclaim_after_break_score": -0.003 + 0.001 * index,
                    "burst_then_fade_score": 0.002 * index,
                    "late_session_integrity_score": 0.01 * index,
                }
            )

    analyzer = V121XCpoRecent1MinPcaStructureAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v121x_cpo_recent_1min_pca_structure_audit_v1",
        result=result,
    )

    assert result.summary["row_count"] == 6
    assert result.summary["feature_count"] == 16
    assert len(result.component_rows) == 2
    assert result.band_rows

    with output_path.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    assert written["summary"]["recommended_next_posture"] == "derive_1min_candidate_microstructure_families_from_pc_structure"
