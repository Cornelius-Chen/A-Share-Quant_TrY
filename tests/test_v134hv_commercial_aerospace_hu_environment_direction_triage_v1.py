from pathlib import Path

from a_share_quant.strategy.v134hv_commercial_aerospace_hu_environment_direction_triage_v1 import (
    V134HVCommercialAerospaceHUEnvironmentDirectionTriageV1Analyzer,
)


def test_v134hv_environment_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134HVCommercialAerospaceHUEnvironmentDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["semantic_count"] == 3
    directions = {row["semantic_name"]: row["direction"] for row in report.triage_rows}
    assert directions["attention_distorted"].startswith("retain_as_primary_negative_environment_semantic")
    assert directions["capital_misaligned_with_board"].startswith("retain_as_primary_negative_environment_semantic")
    assert directions["board_fragile_divergence"] == "retain_as_higher_level_veto_semantic_above_add_reentry"
