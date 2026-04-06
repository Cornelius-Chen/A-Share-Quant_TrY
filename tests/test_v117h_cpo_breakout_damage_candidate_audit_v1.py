from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117h_cpo_breakout_damage_candidate_audit_v1 import (
    V117HCpoBreakoutDamageCandidateAuditAnalyzer,
)


def test_v117h_breakout_damage_candidate_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117HCpoBreakoutDamageCandidateAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117b_payload=json.loads((repo_root / "reports" / "analysis" / "v117b_cpo_cooled_q025_quality_contrast_audit_v1.json").read_text(encoding="utf-8")),
        v117g_payload=json.loads((repo_root / "reports" / "analysis" / "v117g_cpo_breakout_damage_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["candidate_discriminator_name"] == "breakout_damage_containment_score_candidate"
    assert result.summary["captures_quality_signal"] is True
    assert result.summary["replaces_timing_gate"] is False
