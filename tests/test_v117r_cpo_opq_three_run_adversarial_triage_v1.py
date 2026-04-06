from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117r_cpo_opq_three_run_adversarial_triage_v1 import (
    V117RCpoOpqThreeRunAdversarialTriageAnalyzer,
)


def test_v117r_opq_three_run_adversarial_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117RCpoOpqThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117o_payload=json.loads((repo_root / "reports" / "analysis" / "v117o_cpo_breakout_damage_external_pool_audit_v1.json").read_text(encoding="utf-8")),
        v117p_payload=json.loads((repo_root / "reports" / "analysis" / "v117p_cpo_breakout_damage_time_split_external_validation_v1.json").read_text(encoding="utf-8")),
        v117q_payload=json.loads((repo_root / "reports" / "analysis" / "v117q_cpo_breakout_damage_false_positive_explanatory_audit_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["breakout_damage_branch_status"] == "degraded_to_candidate_explanatory_component_only"
    assert result.summary["mainline_investment_allowed"] is False
    assert len(result.triage_rows) == 4
