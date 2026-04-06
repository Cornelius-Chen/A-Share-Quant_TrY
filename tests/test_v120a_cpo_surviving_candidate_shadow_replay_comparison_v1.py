from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v120a_cpo_surviving_candidate_shadow_replay_comparison_v1 import (
    V120ACpoSurvivingCandidateShadowReplayComparisonAnalyzer,
)


def test_v120a_shadow_replay_comparison_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V120ACpoSurvivingCandidateShadowReplayComparisonAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
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
    assert result.summary["candidate_count"] == 4
    assert len(result.candidate_summary_rows) == 4
