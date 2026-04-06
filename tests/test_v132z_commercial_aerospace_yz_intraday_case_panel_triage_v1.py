from pathlib import Path

from a_share_quant.strategy.v132z_commercial_aerospace_yz_intraday_case_panel_triage_v1 import (
    V132ZCommercialAerospaceYZIntradayCasePanelTriageAnalyzer,
)


def test_v132z_intraday_case_panel_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132ZCommercialAerospaceYZIntradayCasePanelTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "retain_intraday_seed_case_panel_as_governance_visual_reference"
    assert report.triage_rows[1]["status"] == "retain_unchanged"
