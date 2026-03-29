from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.feature_pack_b_concept_supported_hierarchy import (
    FeaturePackBConceptSupportedHierarchyAnalyzer,
)


def test_feature_pack_b_concept_supported_hierarchy_detects_bridge_type(tmp_path: Path) -> None:
    report_path = tmp_path / "recheck.json"
    payload = {
        "case_rows": [
            {
                "case_name": "track_b_case",
                "late_quality_straddle": True,
                "non_junk_straddle": False,
                "concept_support": 0.55,
                "primary_concept_weight": 0.60,
                "concept_concentration_ratio": 0.61,
                "challenger_late_quality_margin": -0.03,
                "challenger_non_junk_margin": 0.01,
            },
            {
                "case_name": "track_b_case",
                "late_quality_straddle": True,
                "non_junk_straddle": False,
                "concept_support": 0.52,
                "primary_concept_weight": 0.53,
                "concept_concentration_ratio": 0.55,
                "challenger_late_quality_margin": -0.05,
                "challenger_non_junk_margin": 0.12,
            },
        ]
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = FeaturePackBConceptSupportedHierarchyAnalyzer().analyze(
        recheck_report_path=report_path,
        case_name="track_b_case",
    )

    assert result.summary["dominant_bridge"] == "concept_to_late_mover"
    assert result.summary["concept_supported_late_rows"] == 2
    assert result.summary["concept_supported_non_junk_rows"] == 0
