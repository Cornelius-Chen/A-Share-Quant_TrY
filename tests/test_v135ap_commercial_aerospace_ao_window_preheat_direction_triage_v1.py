from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ap_commercial_aerospace_ao_window_preheat_direction_triage_v1 import (
    V135APCommercialAerospaceAOWindowPreheatDirectionTriageV1Analyzer,
)


def test_v135ap_preheat_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135APCommercialAerospaceAOWindowPreheatDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 1
    assert result.summary["positive_preheat_hold_count"] == 1
    assert result.triage_rows[0]["sample_window_id"] == "ca_train_window_007"
    assert "positive_preheat_sample" in result.triage_rows[0]["recommendation"]
