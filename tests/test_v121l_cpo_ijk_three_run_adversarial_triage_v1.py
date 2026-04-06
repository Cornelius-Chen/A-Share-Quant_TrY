from pathlib import Path

from a_share_quant.strategy.v121l_cpo_ijk_three_run_adversarial_triage_v1 import (
    V121LCpoIJKThreeRunAdversarialTriageAnalyzer,
)


def test_v121l_ijk_three_run_adversarial_triage_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121LCpoIJKThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    assert result.summary["authoritative_status"] in {"candidate_only", "soft_component", "dead"}
    assert result.authoritative_conclusion["replay_facing_allowed"] is False
