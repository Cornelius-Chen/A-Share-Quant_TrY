from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135bb_commercial_aerospace_ba_window_capital_mapping_direction_triage_v1 import (
    V135BBCommercialAerospaceBAWindowCapitalMappingDirectionTriageV1Analyzer,
)


def test_v135bb_window_capital_mapping_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135BBCommercialAerospaceBAWindowCapitalMappingDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 1
    assert result.summary["negative_sample_ready_count"] == 1
    triage_map = {row["sample_window_id"]: row["recommendation"] for row in result.triage_rows}
    assert (
        triage_map["ca_train_window_006"]
        == "allow_negative_training_for_capital_mapping_diffusion_without_structure"
    )
