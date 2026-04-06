from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117e_cpo_continuation_integrity_retained_set_refinement_audit_v1 import (
    V117ECpoContinuationIntegrityRetainedSetRefinementAuditAnalyzer,
)


def test_v117e_retained_set_refinement_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117ECpoContinuationIntegrityRetainedSetRefinementAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117c_payload=json.loads((repo_root / "reports" / "analysis" / "v117c_cpo_quality_side_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["retained_row_count"] == 8
    assert result.summary["retained_positive_count"] > 0
    assert result.summary["retained_weak_count"] > 0
    assert "recommended_next_posture" in result.summary
