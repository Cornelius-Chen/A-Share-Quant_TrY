from pathlib import Path

from a_share_quant.strategy.v127x_commercial_aerospace_xyz_post_promotion_direction_triage_v1 import (
    V127XCommercialAerospaceXYZPostPromotionDirectionTriageAnalyzer,
)


def test_v127x_post_promotion_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127XCommercialAerospaceXYZPostPromotionDirectionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_next_step"] == "stronger_walk_forward_and_robustness_audit"
    assert len(report.subagent_rows) == 3
