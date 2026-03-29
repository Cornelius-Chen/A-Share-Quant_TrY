from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.feature_pack_b_readiness import FeaturePackBReadinessAnalyzer


def test_feature_pack_b_readiness_orders_clean_hierarchy_track_first(tmp_path: Path) -> None:
    triage_path = tmp_path / "triage.json"
    recheck_path = tmp_path / "recheck.json"

    triage_payload = {
        "case_rows": [
            {
                "case_name": "hier_case",
                "triage_classification": "hierarchy_approval_edge",
                "next_focus_features": ["fallback_reason_score"],
            },
            {
                "case_name": "concept_case",
                "triage_classification": "concept_supported_hierarchy_edge",
                "next_focus_features": ["concept_rotation_pressure"],
            },
        ]
    }
    recheck_payload = {
        "case_rows": [
            {
                "case_name": "hier_case",
                "late_quality_straddle": True,
                "non_junk_straddle": True,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": False,
                "challenger_assignment_reason": "fallback_to_junk",
                "concept_support": 0.0,
            },
            {
                "case_name": "hier_case",
                "late_quality_straddle": True,
                "non_junk_straddle": False,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": False,
                "challenger_assignment_reason": "low_composite_or_low_resonance",
                "concept_support": 0.0,
            },
            {
                "case_name": "concept_case",
                "late_quality_straddle": True,
                "non_junk_straddle": False,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": True,
                "challenger_assignment_reason": "fallback_to_junk",
                "concept_support": 0.55,
            },
            {
                "case_name": "concept_case",
                "late_quality_straddle": False,
                "non_junk_straddle": True,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": True,
                "challenger_assignment_reason": "fallback_to_junk",
                "concept_support": 0.52,
            },
        ]
    }

    triage_path.write_text(json.dumps(triage_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    recheck_path.write_text(json.dumps(recheck_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = FeaturePackBReadinessAnalyzer().analyze(
        triage_report_path=triage_path,
        recheck_report_path=recheck_path,
    )

    assert result.summary["first_track"] == "hier_case"
    rows = {row["case_name"]: row for row in result.track_rows}
    assert rows["hier_case"]["dominant_bottleneck"] == "late_quality_and_permission_edge"
    assert rows["concept_case"]["dominant_bottleneck"] == "concept_to_hierarchy_bridge"
