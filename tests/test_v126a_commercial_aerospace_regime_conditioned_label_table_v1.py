from pathlib import Path

from a_share_quant.strategy.v126a_commercial_aerospace_regime_conditioned_label_table_v1 import (
    V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer,
)


def test_v126a_builds_regime_conditioned_labels() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126ACommercialAerospaceRegimeConditionedLabelTableAnalyzer(repo_root).analyze()
    assert result.summary["row_count"] > 0
    assert "de_risk_target" in result.summary["label_counts"]
