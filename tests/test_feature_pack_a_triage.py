from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.feature_pack_a_triage import FeaturePackATriageAnalyzer


def test_feature_pack_a_triage_splits_case_types(tmp_path: Path) -> None:
    report_path = tmp_path / "recheck.json"
    payload = {
        "case_rows": [
            {
                "case_name": "hier_case",
                "dataset_name": "theme_pack",
                "strategy_name": "mainline_trend_b",
                "symbol": "AAA",
                "mechanism_type": "entry_suppression_avoidance",
                "late_quality_straddle": True,
                "non_junk_straddle": True,
                "top_score_straddle": False,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": False,
                "concept_support": 0.0,
                "concept_count": 0,
                "concept_concentration_ratio": 0.0,
            },
            {
                "case_name": "hier_case",
                "dataset_name": "theme_pack",
                "strategy_name": "mainline_trend_b",
                "symbol": "AAA",
                "mechanism_type": "earlier_exit_loss_reduction",
                "late_quality_straddle": True,
                "non_junk_straddle": False,
                "top_score_straddle": False,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": False,
                "concept_support": 0.0,
                "concept_count": 0,
                "concept_concentration_ratio": 0.0,
            },
            {
                "case_name": "concept_case",
                "dataset_name": "theme_pack",
                "strategy_name": "mainline_trend_c",
                "symbol": "BBB",
                "mechanism_type": "entry_suppression_avoidance",
                "late_quality_straddle": True,
                "non_junk_straddle": False,
                "top_score_straddle": False,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": True,
                "concept_support": 0.52,
                "concept_count": 2,
                "concept_concentration_ratio": 0.55,
            },
            {
                "case_name": "concept_case",
                "dataset_name": "theme_pack",
                "strategy_name": "mainline_trend_c",
                "symbol": "BBB",
                "mechanism_type": "delayed_entry_basis_advantage",
                "late_quality_straddle": False,
                "non_junk_straddle": True,
                "top_score_straddle": False,
                "incumbent_permission_allowed": True,
                "challenger_permission_allowed": True,
                "concept_support": 0.58,
                "concept_count": 2,
                "concept_concentration_ratio": 0.61,
            },
        ]
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = FeaturePackATriageAnalyzer().analyze(recheck_report_path=report_path)

    assert result.summary["classification_counts"] == {
        "concept_supported_hierarchy_edge": 1,
        "hierarchy_approval_edge": 1,
    }
    rows = {row["case_name"]: row for row in result.case_rows}
    assert rows["hier_case"]["recommended_track"] == "feature_pack_b_hierarchy_approval"
    assert rows["concept_case"]["recommended_track"] == "feature_pack_b_concept_supported_hierarchy"
