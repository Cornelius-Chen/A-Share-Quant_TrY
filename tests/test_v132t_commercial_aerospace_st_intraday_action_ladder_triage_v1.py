from pathlib import Path

from a_share_quant.strategy.v132t_commercial_aerospace_st_intraday_action_ladder_triage_v1 import (
    V132TCommercialAerospaceSTIntradayActionLadderTriageAnalyzer,
)


def test_v132t_intraday_action_ladder_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132TCommercialAerospaceSTIntradayActionLadderTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "retain_intraday_override_action_ladder_as_governance_state_machine_extension"
    assert report.triage_rows[1]["status"] == "retain_unchanged"
