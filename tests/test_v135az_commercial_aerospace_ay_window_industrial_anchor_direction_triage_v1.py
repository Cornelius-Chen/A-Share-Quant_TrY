from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135az_commercial_aerospace_ay_window_industrial_anchor_direction_triage_v1 import (
    V135AZCommercialAerospaceAYWindowIndustrialAnchorDirectionTriageV1Analyzer,
)


def test_v135az_window_industrial_anchor_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AZCommercialAerospaceAYWindowIndustrialAnchorDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 1
    assert result.summary["negative_support_ready_count"] == 1
    triage_map = {row["sample_window_id"]: row["recommendation"] for row in result.triage_rows}
    assert (
        triage_map["ca_train_window_004"]
        == "allow_negative_support_training_for_real_anchor_but_misaligned_cases"
    )
