from pathlib import Path

from a_share_quant.strategy.v124w_commercial_aerospace_control_extraction_v1 import (
    V124WCommercialAerospaceControlExtractionAnalyzer,
)


def test_v124w_extracts_three_eligibility_names() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124WCommercialAerospaceControlExtractionAnalyzer(repo_root).analyze()
    assert result.summary["eligibility_authority_count"] == 3
