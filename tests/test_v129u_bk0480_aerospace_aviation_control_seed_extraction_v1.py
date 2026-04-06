from pathlib import Path

from a_share_quant.strategy.v129u_bk0480_aerospace_aviation_control_seed_extraction_v1 import (
    V129UBK0480AerospaceAviationControlSeedExtractionAnalyzer,
)


def test_v129u_bk0480_aerospace_aviation_control_seed_extraction_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129UBK0480AerospaceAviationControlSeedExtractionAnalyzer(repo_root).analyze()

    assert result.summary["eligibility_authority_count"] == 1
    assert result.eligibility_rows[0]["symbol"] == "000738"
    assert result.add_permission_rows[0]["symbol"] == "600118"
