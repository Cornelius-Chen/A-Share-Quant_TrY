from pathlib import Path

from a_share_quant.strategy.v121o_cpo_lmn_three_run_adversarial_triage_v1 import (
    V121OCpoLMNThreeRunAdversarialTriageAnalyzer,
)


def test_v121o_lmn_three_run_adversarial_triage_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121OCpoLMNThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    assert result.summary["authoritative_status"] in {"candidate_only", "soft_component", "dead"}
    assert result.authoritative_conclusion["replay_facing_allowed"] is False
