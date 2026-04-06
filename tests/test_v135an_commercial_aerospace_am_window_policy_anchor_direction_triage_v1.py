from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135an_commercial_aerospace_am_window_policy_anchor_direction_triage_v1 import (
    V135ANCommercialAerospaceAMWindowPolicyAnchorDirectionTriageV1Analyzer,
)


def test_v135an_policy_anchor_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135ANCommercialAerospaceAMWindowPolicyAnchorDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 1
    assert result.summary["gate_hold_count"] == 1
    assert result.triage_rows[0]["sample_window_id"] == "ca_train_window_002"
    assert "hold_final_training" in result.triage_rows[0]["recommendation"]
