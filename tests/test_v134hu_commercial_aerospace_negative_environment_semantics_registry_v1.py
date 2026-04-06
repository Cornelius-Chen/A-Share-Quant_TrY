from pathlib import Path

from a_share_quant.strategy.v134hu_commercial_aerospace_negative_environment_semantics_registry_v1 import (
    V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Analyzer,
)


def test_v134hu_negative_environment_semantics_registry() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134HUCommercialAerospaceNegativeEnvironmentSemanticsRegistryV1Analyzer(repo_root).analyze()

    assert report.summary["semantic_count"] == 3
    assert report.summary["primary_semantics_ready_count"] == 3
    names = {row["semantic_name"] for row in report.semantic_rows}
    assert names == {"attention_distorted", "capital_misaligned_with_board", "board_fragile_divergence"}
    for row in report.semantic_rows:
        assert row["phase_status"] == "promote_as_next_main_supervision_target"
        assert row["promotion_boundary"] == "supervision_only"
