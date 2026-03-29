from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.concept_to_late_bridge_analysis import ConceptToLateBridgeAnalyzer


def test_concept_to_late_bridge_analysis_computes_required_uplift(tmp_path: Path) -> None:
    recheck_path = tmp_path / "recheck.json"
    timeline_path = tmp_path / "timeline.yaml"
    derived_path = tmp_path / "derived.yaml"

    recheck_payload = {
        "case_rows": [
            {
                "case_name": "case_a",
                "trigger_date": "2024-05-09",
                "mechanism_type": "entry_suppression_avoidance",
                "late_quality_straddle": True,
                "late_mover_quality": 0.62,
                "concept_support": 0.50,
                "primary_concept_weight": 0.55,
                "concept_concentration_ratio": 0.56,
            }
        ]
    }
    recheck_path.write_text(json.dumps(recheck_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    timeline_path.write_text(
        "\n".join(
            [
                "comparison:",
                "  challenger_candidate: challenger",
                "candidates:",
                "  - candidate_name: challenger",
                "    override:",
                "      trend:",
                "        hierarchy:",
                "          min_quality_for_late_mover: 0.65",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    derived_path.write_text(
        "\n".join(
            [
                "rules:",
                "  concept_support_late_quality_boost: 0.08",
                "  concept_support_band_lower: 0.55",
                "  concept_support_band_upper: 0.60",
                "  concept_support_cap_to_band_upper: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = ConceptToLateBridgeAnalyzer().analyze(
        recheck_report_path=recheck_path,
        case_name="case_a",
        timeline_config_path=timeline_path,
        derived_config_path=derived_path,
    )

    assert result.summary["rows_needing_band_extension"] == 1
    assert result.summary["rows_blocked_by_cap"] == 1
    assert result.summary["max_required_boost_coef"] == 0.06
