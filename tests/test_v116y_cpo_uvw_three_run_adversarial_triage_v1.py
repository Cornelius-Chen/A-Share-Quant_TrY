from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v116y_cpo_uvw_three_run_adversarial_triage_v1 import (
    V116YCpoUvwThreeRunAdversarialTriageAnalyzer,
)


def test_v116y_uvw_three_run_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116YCpoUvwThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116u_payload=json.loads((repo_root / "reports" / "analysis" / "v116u_cpo_expanded_window_action_timepoint_rebuild_v1.json").read_text(encoding="utf-8")),
        v116v_payload=json.loads((repo_root / "reports" / "analysis" / "v116v_cpo_expanded_window_candidate_coverage_reaudit_v1.json").read_text(encoding="utf-8")),
        v116w_payload=json.loads((repo_root / "reports" / "analysis" / "v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1.json").read_text(encoding="utf-8")),
        v116x_payload=json.loads((repo_root / "reports" / "analysis" / "v116x_cpo_rebuilt_new_day_timing_quality_contrast_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["coverage_bug_remaining"] is False
    assert result.summary["authoritative_current_problem"] == "quality_discrimination_after_coverage_repair"
    triage_map = {row["triage_target"]: row for row in result.triage_rows}
    assert triage_map["post_rebuild_coverage_status"]["true_coverage_gap_day_count_after_rebuild"] == 0
    assert triage_map["rebuilt_new_day_contrast"]["2024_01_18_diagnosis"] == "early_visible_and_quality_sufficient_for_corrected_cooled_hit"
