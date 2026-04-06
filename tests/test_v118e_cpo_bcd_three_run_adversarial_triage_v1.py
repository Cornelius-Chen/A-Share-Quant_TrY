from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v118e_cpo_bcd_three_run_adversarial_triage_v1 import (
    V118ECpoBcdThreeRunAdversarialTriageAnalyzer,
)


def test_v118e_bcd_three_run_adversarial_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V118ECpoBcdThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118b_payload=json.loads((repo_root / "reports" / "analysis" / "v118b_cpo_add_vs_entry_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
        v118c_payload=json.loads((repo_root / "reports" / "analysis" / "v118c_cpo_add_vs_entry_external_audit_v1.json").read_text(encoding="utf-8")),
        v118d_payload=json.loads((repo_root / "reports" / "analysis" / "v118d_cpo_add_vs_entry_time_split_validation_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["add_vs_entry_branch_status"] == "retain_candidate_only_for_one_more_non_replay_adversarial_cycle"
    assert result.summary["promotion_allowed"] is False
    assert result.summary["shadow_replay_allowed"] is False
    assert len(result.triage_rows) == 4
