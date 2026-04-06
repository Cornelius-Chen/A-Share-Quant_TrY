from pathlib import Path

from a_share_quant.strategy.v128g_commercial_aerospace_fgh_post_promotion_direction_triage_v1 import (
    V128GCommercialAerospaceFGHPostPromotionDirectionTriageAnalyzer,
)


def test_v128g_post_promotion_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128GCommercialAerospaceFGHPostPromotionDirectionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_next_step"] == "post_window_tail_repair"
