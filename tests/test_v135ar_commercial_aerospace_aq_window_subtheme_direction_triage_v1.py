from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ar_commercial_aerospace_aq_window_subtheme_direction_triage_v1 import (
    V135ARCommercialAerospaceAQWindowSubthemeDirectionTriageV1Analyzer,
)


def test_v135ar_subtheme_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135ARCommercialAerospaceAQWindowSubthemeDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 1
    assert result.summary["negative_sample_ready_count"] == 1
    assert result.triage_rows[0]["sample_window_id"] == "ca_train_window_005"
    assert "negative_sample_training" in result.triage_rows[0]["recommendation"]
