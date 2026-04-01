from pathlib import Path

from a_share_quant.strategy.v116a_three_run_adversarial_review_cadence_protocol_v1 import (
    V116AThreeRunAdversarialReviewCadenceProtocolAnalyzer,
)


def test_v116a_three_run_adversarial_review_cadence_protocol_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116AThreeRunAdversarialReviewCadenceProtocolAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()

    summary = result.summary
    assert summary["acceptance_posture"] == "freeze_v116a_three_run_adversarial_review_cadence_protocol_v1"
    assert summary["cadence_interval_runs"] == 3
    assert summary["required_reviewers"] == 3
    assert summary["current_triage_window_size"] == 3
    assert result.current_triage_window["run_ids"] == ["V115P", "V115Q", "V115R"]
