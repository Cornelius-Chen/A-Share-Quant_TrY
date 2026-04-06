from pathlib import Path

from a_share_quant.strategy.v134fm_commercial_aerospace_fl_module_portability_direction_triage_v1 import (
    V134FMCommercialAerospaceFLModulePortabilityDirectionTriageV1Analyzer,
)


def test_v134fm_commercial_aerospace_fl_module_portability_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FMCommercialAerospaceFLModulePortabilityDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "keep_full_quality_add_archetype_local_only_and_block_module_promotion"
    )
