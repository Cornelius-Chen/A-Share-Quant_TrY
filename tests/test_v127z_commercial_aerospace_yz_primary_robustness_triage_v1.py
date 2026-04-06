from pathlib import Path

from a_share_quant.strategy.v127z_commercial_aerospace_yz_primary_robustness_triage_v1 import (
    V127ZCommercialAerospaceYZPrimaryRobustnessTriageAnalyzer,
)


def test_v127z_primary_robustness_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127ZCommercialAerospaceYZPrimaryRobustnessTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "freeze_current_primary_after_robustness"
    assert report.summary["authoritative_next_step"] == "return_to_primary_reference_attribution_and_understanding"
