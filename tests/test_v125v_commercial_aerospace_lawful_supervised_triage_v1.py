from pathlib import Path

from a_share_quant.strategy.v125v_commercial_aerospace_lawful_supervised_triage_v1 import (
    V125VCommercialAerospaceLawfulSupervisedTriageAnalyzer,
)


def test_v125v_freezes_eod_only_status() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125VCommercialAerospaceLawfulSupervisedTriageAnalyzer(repo_root).analyze()
    assert result.summary["eod_lawful"] is True
    assert result.summary["intraday_lawful"] is False
