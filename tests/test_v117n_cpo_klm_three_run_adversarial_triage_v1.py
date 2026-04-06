from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117n_cpo_klm_three_run_adversarial_triage_v1 import (
    V117NCpoKlmThreeRunAdversarialTriageAnalyzer,
)


def test_v117n_klm_three_run_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117NCpoKlmThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117k_payload=json.loads((repo_root / "reports" / "analysis" / "v117k_cpo_reverse_signal_candidate_discovery_v1.json").read_text(encoding="utf-8")),
        v117l_payload=json.loads((repo_root / "reports" / "analysis" / "v117l_cpo_human_heuristic_signal_quantization_protocol_v1.json").read_text(encoding="utf-8")),
        v117m_payload=json.loads((repo_root / "reports" / "analysis" / "v117m_cpo_reverse_signal_context_conditioning_audit_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["reverse_signal_branch_status"] == "degraded_to_secondary_explanatory_drawdown_component"
    assert result.summary["human_heuristic_quantization_status"] == "protocol_only_not_mainline_training_asset"
    assert result.summary["promotion_allowed"] is False
