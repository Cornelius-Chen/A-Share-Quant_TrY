from pathlib import Path

from a_share_quant.strategy.v124v_commercial_aerospace_control_core_thinning_retriage_v1 import (
    V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer,
)


def test_v124v_keeps_only_formal_group_in_control_core() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124VCommercialAerospaceControlCoreThinningRetriageAnalyzer(repo_root).analyze()
    assert result.summary["control_core_count"] > 0
    assert all(row["group"] == "正式组" for row in result.control_core_rows)
