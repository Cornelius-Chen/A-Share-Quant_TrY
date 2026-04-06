from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117z_cpo_wxy_three_run_adversarial_triage_v1 import (
    V117ZCpoWxyThreeRunAdversarialTriageAnalyzer,
)


def test_v117z_wxy_three_run_adversarial_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117ZCpoWxyThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117w_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        v117x_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v117x_cpo_cooling_reacceleration_false_positive_control_external_audit_v1.json").read_text(
                encoding="utf-8"
            )
        ),
        v117y_payload=json.loads(
            (repo_root / "reports" / "analysis" / "v117y_cpo_cooling_reacceleration_false_positive_control_time_split_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    )

    assert result.summary["cooling_reacceleration_branch_status"] == "retain_candidate_only_continue_without_shadow_replay"
    assert result.summary["promotion_allowed"] is False
    assert result.summary["shadow_replay_allowed"] is False
    assert result.summary["candidate_only_allowed"] is True
    assert len(result.triage_rows) == 4
