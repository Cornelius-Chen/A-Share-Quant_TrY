import json
from pathlib import Path

from a_share_quant.strategy.v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1 import (
    V116WCpoCorrectedCooledShadowExpandedWindowValidationRebuiltBaseAnalyzer,
)


def test_v116w_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116WCpoCorrectedCooledShadowExpandedWindowValidationRebuiltBaseAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        rebuilt_pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
        training_view_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        feature_base_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["acceptance_posture"] == "freeze_v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1"
    assert result.summary["candidate_base_source"] == "rebuilt_expanded_window_pca_band_rows"
