from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117b_cpo_cooled_q025_quality_contrast_audit_v1 import (
    V117BCpoCooledQ025QualityContrastAuditAnalyzer,
)


def test_v117b_quality_contrast_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117BCpoCooledQ025QualityContrastAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116x_payload=json.loads((repo_root / "reports" / "analysis" / "v116x_cpo_rebuilt_new_day_timing_quality_contrast_v1.json").read_text(encoding="utf-8")),
        v117a_payload=json.loads((repo_root / "reports" / "analysis" / "v117a_cpo_quality_side_cooled_retention_v1.json").read_text(encoding="utf-8")),
        rebuilt_rows_path=repo_root / "data" / "training" / "cpo_midfreq_expanded_window_rebuilt_rows_v1.csv",
    )

    row_map = {row["signal_trade_date"]: row for row in result.contrast_rows}
    assert row_map["2024-01-18"]["final_judgement"] == "retained_quality_standard_met"
    assert row_map["2023-11-07"]["final_judgement"] == "late_visibility_blocks_otherwise_good_day"
    assert row_map["2024-01-23"]["final_judgement"] == "late_and_quality_weak"
