from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117v_cpo_stu_three_run_adversarial_triage_v1 import (
    V117VCpoStuThreeRunAdversarialTriageAnalyzer,
)


def test_v117v_stu_three_run_adversarial_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117VCpoStuThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117s_payload=json.loads((repo_root / "reports" / "analysis" / "v117s_cpo_cooling_reacceleration_discovery_v1.json").read_text(encoding="utf-8")),
        v117t_payload=json.loads((repo_root / "reports" / "analysis" / "v117t_cpo_cooling_reacceleration_external_audit_v1.json").read_text(encoding="utf-8")),
        v117u_payload=json.loads((repo_root / "reports" / "analysis" / "v117u_cpo_cooling_reacceleration_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["cooling_reacceleration_branch_status"] == "retain_candidate_only_continue_one_more_non_replay_audit_cycle"
    assert result.summary["promotion_allowed"] is False
    assert result.summary["replay_facing_expansion_allowed"] is False
    assert len(result.triage_rows) == 4
