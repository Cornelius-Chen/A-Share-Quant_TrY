from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117f_cpo_cde_three_run_adversarial_triage_v1 import (
    V117FCpoCdeThreeRunAdversarialTriageAnalyzer,
)


def test_v117f_cde_three_run_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117FCpoCdeThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117c_payload=json.loads((repo_root / "reports" / "analysis" / "v117c_cpo_quality_side_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
        v117d_payload=json.loads((repo_root / "reports" / "analysis" / "v117d_cpo_continuation_integrity_candidate_audit_v1.json").read_text(encoding="utf-8")),
        v117e_payload=json.loads((repo_root / "reports" / "analysis" / "v117e_cpo_continuation_integrity_retained_set_refinement_audit_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["continuation_integrity_candidate_status"] == "degraded_to_explanatory_component_only"
    assert result.summary["promotion_allowed"] is False
    assert result.summary["new_standalone_gate_allowed"] is False
