from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v118i_cpo_fgh_three_run_adversarial_triage_v1 import (
    V118ICpoFghThreeRunAdversarialTriageAnalyzer,
)


def test_v118i_fgh_three_run_adversarial_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V118ICpoFghThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v118f_payload=json.loads((repo_root / "reports" / "analysis" / "v118f_cpo_add_vs_strong_entry_external_audit_v1.json").read_text(encoding="utf-8")),
        v118g_payload=json.loads((repo_root / "reports" / "analysis" / "v118g_cpo_add_vs_entry_role_family_holdout_v1.json").read_text(encoding="utf-8")),
        v118h_payload=json.loads((repo_root / "reports" / "analysis" / "v118h_cpo_add_vs_entry_role_year_entanglement_audit_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["add_vs_entry_branch_status"] == "degraded_to_explanatory_only"
    assert result.summary["candidate_only_allowed"] is False
    assert result.summary["explanatory_only_allowed"] is True
    assert len(result.triage_rows) == 4
