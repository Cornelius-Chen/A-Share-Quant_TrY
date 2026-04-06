from pathlib import Path

from a_share_quant.strategy.v127f_commercial_aerospace_def_orthogonal_downside_promotion_triage_v1 import (
    V127FCommercialAerospaceDEFOrthogonalDownsidePromotionTriageAnalyzer,
)


def test_v127f_orthogonal_downside_promotion_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127FCommercialAerospaceDEFOrthogonalDownsidePromotionTriageAnalyzer(repo_root).analyze()
    assert result.summary["broad_beats_old_reference"] is True
    assert result.summary["broad_beats_cleaner_reference"] is True
