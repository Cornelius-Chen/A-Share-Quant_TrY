from pathlib import Path

from a_share_quant.strategy.v127w_commercial_aerospace_wxy_window_derisk_promotion_triage_v1 import (
    V127WCommercialAerospaceWXYWindowDeriskPromotionTriageAnalyzer,
)


def test_v127w_window_derisk_promotion_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127WCommercialAerospaceWXYWindowDeriskPromotionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "promote_window_specific_derisk_fix_to_primary_reference"
    assert report.summary["new_primary_variant"] == "window_riskoff_full_weakdrift_075_impulse_half"
