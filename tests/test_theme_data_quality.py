from __future__ import annotations

from a_share_quant.data.theme_data_quality import ThemeDataQualityAnalyzer


def test_theme_data_quality_analyzer_flags_static_and_sparse_concepts() -> None:
    result = ThemeDataQualityAnalyzer().analyze(
        security_master_rows=[
            {"symbol": "AAA"},
            {"symbol": "BBB"},
            {"symbol": "CCC"},
        ],
        concept_mapping_rows=[
            {
                "symbol": "AAA",
                "concept_name": "AI",
                "is_primary_concept": "true",
                "weight": "1.0",
            },
            {
                "symbol": "AAA",
                "concept_name": "AI",
                "is_primary_concept": "true",
                "weight": "1.0",
            },
            {
                "symbol": "BBB",
                "concept_name": "AI",
                "is_primary_concept": "true",
                "weight": "1.0",
            },
        ],
        sector_mapping_rows=[
            {"sector_name": "AI"},
            {"sector_name": "AI"},
        ],
    )

    assert result.summary["concept_symbol_coverage_ratio"] == 0.666667
    assert result.summary["static_primary_symbol_ratio"] == 1.0
    warning_types = {warning["type"] for warning in result.warnings}
    assert "coverage_gap" in warning_types
    assert "static_primary_concepts" in warning_types
    assert "concept_concentration" in warning_types
