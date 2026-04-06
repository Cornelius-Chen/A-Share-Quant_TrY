from pathlib import Path

from a_share_quant.strategy.v132j_commercial_aerospace_ij_local_1min_false_positive_triage_v1 import (
    V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageAnalyzer,
)


def test_v132j_local_1min_false_positive_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132JCommercialAerospaceIJLocal1MinFalsePositiveTriageAnalyzer(repo_root).analyze()

    assert result.summary["seed_match_count"] == result.summary["seed_row_count"]
