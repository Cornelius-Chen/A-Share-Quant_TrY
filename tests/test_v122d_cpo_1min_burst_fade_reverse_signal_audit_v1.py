from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v122d_cpo_1min_burst_fade_reverse_signal_audit_v1 import (
    V122DCpo1MinBurstFadeReverseSignalAuditAnalyzer,
    write_report,
)


def test_v122d_cpo_1min_burst_fade_reverse_signal_audit(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports" / "analysis"
    reports_dir.mkdir(parents=True, exist_ok=True)
    training_dir = tmp_path / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)

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
        for symbol in ["300308", "300502"]:
            for index in range(8):
                writer.writerow(
                    {
                        "symbol": symbol,
                        "bar_time": f"2026-04-03 10:{index:02d}:00",
                        "trade_date": "2026-04-03",
                        "clock_time": f"10:{index:02d}:00",
                        "minute_index": index,
                        "is_late_session": 0,
                        "open": 10 - index * 0.1,
                        "high": 10.1 - index * 0.1,
                        "low": 9.7 - index * 0.1,
                        "close": 9.95 - index * 0.1,
                        "volume": 1000,
                        "amount": 10000,
                        "minute_return": -0.001 * index,
                        "range_pct": 0.02,
                        "body_pct": -0.01,
                        "upper_shadow_pct": 0.01,
                        "lower_shadow_pct": 0.001,
                        "close_location": 0.2,
                        "close_vs_vwap": -0.01,
                        "pullback_from_high": -0.02,
                        "push_efficiency": -0.8,
                        "micro_pullback_depth": 0.01,
                        "volume_ratio_5": 2.0,
                        "value_ratio_5": 2.0,
                        "prev_close_gap": -0.001,
                        "reclaim_after_break_score": -0.002,
                        "burst_then_fade_score": 0.002,
                        "late_session_integrity_score": -0.1,
                    }
                )

    analyzer = V122DCpo1MinBurstFadeReverseSignalAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=reports_dir,
        report_name="v122d_cpo_1min_burst_fade_reverse_signal_audit_v1",
        result=result,
    )
    assert output_path.exists()
    assert result.summary["symbol_count"] >= 1
