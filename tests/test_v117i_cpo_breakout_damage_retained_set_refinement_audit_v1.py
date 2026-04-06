from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117i_cpo_breakout_damage_retained_set_refinement_audit_v1 import (
    V117ICpoBreakoutDamageRetainedSetRefinementAuditAnalyzer,
)


def test_v117i_breakout_damage_retained_refinement() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117ICpoBreakoutDamageRetainedSetRefinementAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117g_payload=json.loads((repo_root / "reports" / "analysis" / "v117g_cpo_breakout_damage_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["retained_row_count"] == 8
    assert result.summary["retained_positive_count"] > 0
    assert result.summary["retained_weak_count"] > 0
