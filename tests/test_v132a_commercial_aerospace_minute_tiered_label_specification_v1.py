from pathlib import Path

from a_share_quant.strategy.v132a_commercial_aerospace_minute_tiered_label_specification_v1 import (
    V132ACommercialAerospaceMinuteTieredLabelSpecificationAnalyzer,
)


def test_v132a_minute_tiered_label_specification() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132ACommercialAerospaceMinuteTieredLabelSpecificationAnalyzer(repo_root).analyze()

    assert result.summary["registry_row_count"] == 6
    assert result.summary["severity_tier_count"] == 3
    assert len(result.proposed_label_rules) == 3

