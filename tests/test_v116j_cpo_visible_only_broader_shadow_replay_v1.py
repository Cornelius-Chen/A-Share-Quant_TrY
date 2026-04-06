from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v116j_cpo_visible_only_broader_shadow_replay_v1 import (
    V116JCpoVisibleOnlyBroaderShadowReplayAnalyzer,
)


def test_v116j_visible_only_broader_shadow_replay_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116JCpoVisibleOnlyBroaderShadowReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v114x_payload=json.loads((repo_root / "reports" / "analysis" / "v114x_cpo_probability_expectancy_sizing_framework_repaired_v1.json").read_text(encoding="utf-8")),
        v116d_payload=json.loads((repo_root / "reports" / "analysis" / "v116d_cpo_visible_only_intraday_filter_refinement_v1.json").read_text(encoding="utf-8")),
        pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
        training_view_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        feature_base_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )

    assert result.summary["acceptance_posture"] == "freeze_v116j_cpo_visible_only_broader_shadow_replay_v1"
    assert result.summary["wider_candidate_row_count"] >= 1
    assert result.summary["shadow_replay_final_equity"] >= result.summary["baseline_final_equity"]
    assert result.summary["executed_overlay_order_count"] >= 1
    assert any(row["timing_bucket"] == "intraday_same_session" for row in result.timing_rows)
