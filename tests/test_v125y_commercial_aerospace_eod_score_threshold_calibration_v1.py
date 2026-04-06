from pathlib import Path

from a_share_quant.strategy.v125y_commercial_aerospace_eod_score_threshold_calibration_v1 import (
    V125YCommercialAerospaceEODScoreThresholdCalibrationAnalyzer,
)


def test_v125y_runs_threshold_calibration() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125YCommercialAerospaceEODScoreThresholdCalibrationAnalyzer(repo_root).analyze()
    assert result.summary["test_row_count"] > 0
