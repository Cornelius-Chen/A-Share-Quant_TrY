from pathlib import Path

from a_share_quant.strategy.v126m_commercial_aerospace_phase_geometry_label_table_v1 import (
    V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer,
)


def test_v126m_phase_geometry_label_table_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126MCommercialAerospacePhaseGeometryLabelTableAnalyzer(repo_root).analyze()
    assert result.summary["row_count"] > 0
    assert result.summary["full_preheat_count"] > 0
