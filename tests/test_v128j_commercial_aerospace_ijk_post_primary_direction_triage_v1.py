from pathlib import Path

from a_share_quant.strategy.v128j_commercial_aerospace_ijk_post_primary_direction_triage_v1 import (
    V128JCommercialAerospaceIJKPostPrimaryDirectionTriageAnalyzer,
)


def test_v128j_post_primary_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128JCommercialAerospaceIJKPostPrimaryDirectionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_next_step"] == "stop_local_micro_tuning_and_begin_portability_packaging"
