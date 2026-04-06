from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135at_commercial_aerospace_as_window_cross_narrative_direction_triage_v1 import (
    V135ATCommercialAerospaceASWindowCrossNarrativeDirectionTriageV1Analyzer,
)


def test_v135at_cross_narrative_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135ATCommercialAerospaceASWindowCrossNarrativeDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 1
    assert result.summary["bridge_sample_ready_count"] == 1
    assert result.triage_rows[0]["sample_window_id"] == "ca_train_window_009"
    assert "bridge_sample" in result.triage_rows[0]["recommendation"]
