from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v117m_cpo_reverse_signal_context_conditioning_audit_v1 import (
    V117MCpoReverseSignalContextConditioningAuditAnalyzer,
)


def test_v117m_reverse_signal_context_conditioning() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117MCpoReverseSignalContextConditioningAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_expanded_window_rebuilt_v1.csv",
        v117k_payload=json.loads((repo_root / "reports" / "analysis" / "v117k_cpo_reverse_signal_candidate_discovery_v1.json").read_text(encoding="utf-8")),
    )

    assert result.summary["conditioned_row_count"] > 0
    assert result.summary["conditioned_negative_count"] > 0
    assert result.summary["conditioned_non_negative_count"] > 0
