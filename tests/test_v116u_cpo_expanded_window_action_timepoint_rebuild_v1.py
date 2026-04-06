import json
from pathlib import Path

from a_share_quant.strategy.v116u_cpo_expanded_window_action_timepoint_rebuild_v1 import (
    V116UCpoExpandedWindowActionTimepointRebuildAnalyzer,
)


def test_v116u_expanded_window_action_timepoint_rebuild_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116UCpoExpandedWindowActionTimepointRebuildAnalyzer(repo_root=repo_root)
    result, rebuilt_rows, merged_rows = analyzer.analyze(
        v116s_payload=json.loads((repo_root / "reports" / "analysis" / "v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1.json").read_text(encoding="utf-8")),
        original_pca_rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
        training_view_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv",
        feature_base_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        daily_bar_path=repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv",
    )
    assert result.summary["acceptance_posture"] == "freeze_v116u_cpo_expanded_window_action_timepoint_rebuild_v1"
    assert result.summary["rebuilt_day_count"] == 3
    assert len(rebuilt_rows) >= 6
    assert len(merged_rows) >= len(rebuilt_rows)
