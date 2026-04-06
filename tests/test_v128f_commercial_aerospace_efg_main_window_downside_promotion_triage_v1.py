from pathlib import Path

from a_share_quant.strategy.v128f_commercial_aerospace_efg_main_window_downside_promotion_triage_v1 import (
    V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageAnalyzer,
)


def test_v128f_main_window_downside_promotion_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "promote_main_window_downside_variant_to_primary_reference"
    assert report.summary["new_primary_variant"] == "mainwin_overdrive_075_impulse_075"
