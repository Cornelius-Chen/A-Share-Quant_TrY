from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117d_cpo_continuation_integrity_candidate_audit_v1 import (
    V117DCpoContinuationIntegrityCandidateAuditAnalyzer,
)


def test_v117d_continuation_integrity_candidate_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117DCpoContinuationIntegrityCandidateAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v117b_payload=json.loads((repo_root / "reports" / "analysis" / "v117b_cpo_cooled_q025_quality_contrast_audit_v1.json").read_text(encoding="utf-8")),
        v117c_payload=json.loads((repo_root / "reports" / "analysis" / "v117c_cpo_quality_side_discriminator_discovery_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["candidate_discriminator_name"] == "continuation_integrity_score_candidate"
    assert result.summary["captures_quality_signal"] is True
    assert result.summary["replaces_timing_gate"] is False
    assert result.summary["standalone_threshold_usable_now"] is False
    assert result.summary["retained_day_passes_quality_gate"] is False
