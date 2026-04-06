from pathlib import Path

from a_share_quant.strategy.v121s_cpo_pqr_three_run_adversarial_triage_v1 import (
    V121SCpoPQRThreeRunAdversarialTriageAnalyzer,
)


def test_v121s_pqr_three_run_adversarial_triage_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121SCpoPQRThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    assert result.summary["authoritative_status"] == "explanatory_only"
    assert result.authoritative_conclusion["replay_facing_allowed"] is False
