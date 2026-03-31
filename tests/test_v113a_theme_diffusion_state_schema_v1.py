from pathlib import Path

from a_share_quant.strategy.v113a_theme_diffusion_state_schema_v1 import (
    V113AThemeDiffusionStateSchemaAnalyzer,
    load_json_report,
)


def test_v113a_theme_diffusion_state_schema_v1_freezes_core_layers() -> None:
    result = V113AThemeDiffusionStateSchemaAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v113a_phase_charter_v1.json"))
    )
    assert result.summary["phase_state_count"] == 4
    assert result.summary["stock_role_count"] == 4
    assert result.summary["strength_dimension_count"] == 4
    assert result.summary["driver_dimension_count"] == 4
    assert result.summary["review_only_candidate_driver_count"] == 10
