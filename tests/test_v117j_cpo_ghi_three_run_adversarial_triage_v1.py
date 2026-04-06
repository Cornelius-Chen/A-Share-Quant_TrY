from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117j_cpo_ghi_three_run_adversarial_triage_v1 import (
    V117JCpoGhiThreeRunAdversarialTriageAnalyzer,
)


def test_v117j_ghi_three_run_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117JCpoGhiThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117g_payload=json.loads((repo_root / "reports" / "analysis" / "v117g_cpo_breakout_damage_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
        v117h_payload=json.loads((repo_root / "reports" / "analysis" / "v117h_cpo_breakout_damage_candidate_audit_v1.json").read_text(encoding="utf-8")),
        v117i_payload=json.loads((repo_root / "reports" / "analysis" / "v117i_cpo_breakout_damage_retained_set_refinement_audit_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["breakout_damage_branch_status"] == "retain_candidate_only_continue_external_audit"
    assert result.summary["promotion_allowed"] is False
    assert result.summary["new_quality_branch_alive"] is True
