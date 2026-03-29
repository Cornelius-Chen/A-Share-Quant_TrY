from __future__ import annotations

from a_share_quant.strategy.u1_lightweight_geometry import U1LightweightGeometryAnalyzer


def test_u1_lightweight_geometry_detects_case_separation() -> None:
    payload = {
        "case_rows": [
            {
                "case_name": "case_a",
                "symbol": "AAA",
                "trigger_date": "2024-01-01",
                "mechanism_type": "m1",
                "challenger_margin_gap": -0.1,
                "fallback_reason_score": 0.02,
                "top_score_gap": 0.6,
                "challenger_top_score_gap": 2.5,
                "challenger_late_quality_margin": -0.08,
                "challenger_non_junk_margin": 0.15,
                "challenger_resonance_margin": 0.08,
                "concept_support": 0.0,
                "primary_concept_weight": 0.0,
                "concept_count": 0,
                "concept_concentration_ratio": 0.0,
            },
            {
                "case_name": "case_a",
                "symbol": "AAA",
                "trigger_date": "2024-01-02",
                "mechanism_type": "m2",
                "challenger_margin_gap": -0.09,
                "fallback_reason_score": 0.01,
                "top_score_gap": 0.5,
                "challenger_top_score_gap": 2.3,
                "challenger_late_quality_margin": -0.07,
                "challenger_non_junk_margin": 0.14,
                "challenger_resonance_margin": 0.07,
                "concept_support": 0.0,
                "primary_concept_weight": 0.0,
                "concept_count": 0,
                "concept_concentration_ratio": 0.0,
            },
            {
                "case_name": "case_b",
                "symbol": "BBB",
                "trigger_date": "2024-02-01",
                "mechanism_type": "m3",
                "challenger_margin_gap": 0.4,
                "fallback_reason_score": 0.05,
                "top_score_gap": 1.2,
                "challenger_top_score_gap": 1.0,
                "challenger_late_quality_margin": -0.03,
                "challenger_non_junk_margin": 0.01,
                "challenger_resonance_margin": 0.0,
                "concept_support": 0.6,
                "primary_concept_weight": 0.58,
                "concept_count": 2,
                "concept_concentration_ratio": 0.55,
            },
            {
                "case_name": "case_b",
                "symbol": "BBB",
                "trigger_date": "2024-02-02",
                "mechanism_type": "m4",
                "challenger_margin_gap": 0.35,
                "fallback_reason_score": 0.04,
                "top_score_gap": 1.1,
                "challenger_top_score_gap": 1.1,
                "challenger_late_quality_margin": -0.02,
                "challenger_non_junk_margin": 0.02,
                "challenger_resonance_margin": 0.01,
                "concept_support": 0.55,
                "primary_concept_weight": 0.53,
                "concept_count": 2,
                "concept_concentration_ratio": 0.52,
            },
        ]
    }
    feature_names = [
        "challenger_margin_gap",
        "fallback_reason_score",
        "top_score_gap",
        "challenger_top_score_gap",
        "challenger_late_quality_margin",
        "challenger_non_junk_margin",
        "challenger_resonance_margin",
        "concept_support",
        "primary_concept_weight",
        "concept_count",
        "concept_concentration_ratio",
    ]

    result = U1LightweightGeometryAnalyzer().analyze(
        recheck_payload=payload,
        feature_names=feature_names,
    )

    assert result.summary["case_count"] == 2
    assert result.summary["active_feature_count"] >= 5
    assert result.summary["pc1_explained_variance_ratio"] > 0.5
    assert result.summary["separation_reading"] == "cases_geometrically_separable"
