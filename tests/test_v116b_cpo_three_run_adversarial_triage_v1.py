from pathlib import Path

from a_share_quant.strategy.v116b_cpo_three_run_adversarial_triage_v1 import (
    V116BCpoThreeRunAdversarialTriageAnalyzer,
)


def test_v116b_three_run_adversarial_triage_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116BCpoThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()

    summary = result.summary
    assert summary["acceptance_posture"] == "freeze_v116b_cpo_three_run_adversarial_triage_v1"
    assert summary["triage_window"] == ["V115P", "V115Q", "V115R"]
    assert summary["reviewer_count"] == 3
    assert summary["retained_conclusion_count"] >= 1
    assert summary["do_not_promote_count"] >= 1
    assert summary["hard_constraint_count"] >= 1
