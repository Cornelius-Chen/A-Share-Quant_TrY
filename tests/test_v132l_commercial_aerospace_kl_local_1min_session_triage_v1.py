from pathlib import Path

from a_share_quant.strategy.v132l_commercial_aerospace_kl_local_1min_session_triage_v1 import (
    V132LCommercialAerospaceKLLocal1MinSessionTriageAnalyzer,
)


def test_v132l_local_1min_session_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132LCommercialAerospaceKLLocal1MinSessionTriageAnalyzer(repo_root).analyze()

    assert result.summary["expanded_session_count"] == 612
