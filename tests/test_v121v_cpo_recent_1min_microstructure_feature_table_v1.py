from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v121v_cpo_recent_1min_microstructure_feature_table_v1 import (
    V121VCpoRecent1MinMicrostructureFeatureTableAnalyzer,
    write_report,
)


def test_v121v_cpo_recent_1min_microstructure_feature_table(tmp_path: Path) -> None:
    repo_root = tmp_path
    minute_dir = repo_root / "data" / "raw" / "minute_bars"
    minute_dir.mkdir(parents=True, exist_ok=True)
    sample_path = minute_dir / "sina_300308_recent_1min_v1.csv"
    with sample_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["day", "open", "high", "low", "close", "volume", "amount"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "day": "2026-04-03 10:30:00",
                "open": 10.0,
                "high": 10.5,
                "low": 9.8,
                "close": 10.4,
                "volume": 1000,
                "amount": 10400,
            }
        )
        writer.writerow(
            {
                "day": "2026-04-03 10:31:00",
                "open": 10.4,
                "high": 10.6,
                "low": 10.2,
                "close": 10.3,
                "volume": 1200,
                "amount": 12360,
            }
        )

    analyzer = V121VCpoRecent1MinMicrostructureFeatureTableAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121v_cpo_recent_1min_microstructure_feature_table_v1",
        result=result,
    )

    assert result.summary["symbol_count"] == 1
    assert result.summary["total_row_count"] == 2
    assert output_path.exists()

    feature_table = repo_root / "data" / "training" / "cpo_recent_1min_microstructure_feature_table_v1.csv"
    with feature_table.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 2
    assert "close_vs_vwap" in rows[0]
    assert "upper_shadow_pct" in rows[0]
    assert "reclaim_after_break_score" in rows[1]

    with output_path.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    assert written["summary"]["recommended_next_posture"] == "start_1min_microstructure_discovery_on_core_names"
