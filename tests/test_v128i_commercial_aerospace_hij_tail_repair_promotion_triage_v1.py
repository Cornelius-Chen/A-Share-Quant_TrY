from pathlib import Path

from a_share_quant.strategy.v128i_commercial_aerospace_hij_tail_repair_promotion_triage_v1 import (
    V128ICommercialAerospaceHIJTailRepairPromotionTriageAnalyzer,
)


def test_v128i_tail_repair_promotion_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128ICommercialAerospaceHIJTailRepairPromotionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "promote_tail_weakdrift_full_to_primary_reference"
    assert report.summary["new_primary_variant"] == "tail_weakdrift_full"
