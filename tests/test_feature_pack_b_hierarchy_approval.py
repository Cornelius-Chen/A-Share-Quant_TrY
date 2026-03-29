from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.feature_pack_b_hierarchy_approval import (
    FeaturePackBHierarchyApprovalAnalyzer,
)


def test_feature_pack_b_hierarchy_approval_detects_coupled_edge(tmp_path: Path) -> None:
    report_path = tmp_path / "recheck.json"
    payload = {
        "case_rows": [
            {
                "case_name": "track_a_case",
                "late_quality_straddle": True,
                "non_junk_straddle": False,
                "margin_straddle": False,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": False,
                "challenger_assignment_reason": "fallback_to_junk",
                "fallback_reason_score": 0.05,
                "challenger_margin_gap": -0.03,
                "challenger_late_quality_margin": -0.08,
            },
            {
                "case_name": "track_a_case",
                "late_quality_straddle": True,
                "non_junk_straddle": True,
                "margin_straddle": False,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": True,
                "challenger_assignment_reason": "low_composite_or_low_resonance",
                "fallback_reason_score": 0.04,
                "challenger_margin_gap": 0.12,
                "challenger_late_quality_margin": -0.06,
            },
        ]
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = FeaturePackBHierarchyApprovalAnalyzer().analyze(
        recheck_report_path=report_path,
        case_name="track_a_case",
    )

    assert result.summary["dominant_hierarchy_edge"] == "late_mover_quality"
    assert result.summary["dominant_approval_edge"] == "permission_state_divergence"
    assert result.summary["permission_split_rows"] == 1
