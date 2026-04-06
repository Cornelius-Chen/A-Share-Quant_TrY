from pathlib import Path

from a_share_quant.strategy.v126u_commercial_aerospace_stu_preheat_tier_triage_v1 import (
    V126UCommercialAerospaceSTUPreheatTierTriageAnalyzer,
)


def test_v126u_preheat_tier_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126UCommercialAerospaceSTUPreheatTierTriageAnalyzer(repo_root).analyze()
    assert result.summary["preheat_tier_v126t_final_equity"] > 0
