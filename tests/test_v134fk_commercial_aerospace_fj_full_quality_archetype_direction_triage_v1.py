from pathlib import Path

from a_share_quant.strategy.v134fk_commercial_aerospace_fj_full_quality_archetype_direction_triage_v1 import (
    V134FKCommercialAerospaceFJFullQualityArchetypeDirectionTriageV1Analyzer,
)


def test_v134fk_commercial_aerospace_fj_full_quality_archetype_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FKCommercialAerospaceFJFullQualityArchetypeDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_full_quality_add_archetype_as_local_supervision_anchor_only"
    )
