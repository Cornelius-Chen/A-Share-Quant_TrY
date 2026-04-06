from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v120a_cpo_surviving_candidate_shadow_replay_comparison_v1 import (
    V120ACpoSurvivingCandidateShadowReplayComparisonAnalyzer,
)
from a_share_quant.strategy.v120b_cpo_surviving_candidate_shadow_replay_plots_v1 import (
    V120BCpoSurvivingCandidateShadowReplayPlotsAnalyzer,
)


def test_v120b_shadow_replay_plots_run() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    comparison = V120ACpoSurvivingCandidateShadowReplayComparisonAnalyzer(repo_root=repo_root).analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v116z_payload=json.loads((repo_root / "reports" / "analysis" / "v116z_cpo_quality_side_cooled_refinement_v1.json").read_text(encoding="utf-8")),
        v117a_payload=json.loads((repo_root / "reports" / "analysis" / "v117a_cpo_quality_side_cooled_retention_v1.json").read_text(encoding="utf-8")),
        v117w_payload=json.loads((repo_root / "reports" / "analysis" / "v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1.json").read_text(encoding="utf-8")),
        v117x_payload=json.loads((repo_root / "reports" / "analysis" / "v117x_cpo_cooling_reacceleration_false_positive_control_external_audit_v1.json").read_text(encoding="utf-8")),
        v118u_payload=json.loads((repo_root / "reports" / "analysis" / "v118u_cpo_sustained_participation_non_chase_external_audit_v1.json").read_text(encoding="utf-8")),
        v119l_payload=json.loads((repo_root / "reports" / "analysis" / "v119l_cpo_participation_turnover_elg_support_discovery_v1.json").read_text(encoding="utf-8")),
        v119m_payload=json.loads((repo_root / "reports" / "analysis" / "v119m_cpo_participation_turnover_elg_support_external_audit_v1.json").read_text(encoding="utf-8")),
    )
    plots = V120BCpoSurvivingCandidateShadowReplayPlotsAnalyzer(repo_root=repo_root).analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v120a_payload=comparison.as_dict(),
    )
    assert plots.summary["candidate_count_plotted"] >= 1
