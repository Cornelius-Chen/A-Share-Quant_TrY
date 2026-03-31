from pathlib import Path

from a_share_quant.strategy.v112ac_phase_check_v1 import (
    V112ACPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ac_phase_check_keeps_unsupervised_probe_review_only() -> None:
    analyzer = V112ACPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ac_phase_charter_v1.json")),
        challenge_probe_payload=load_json_report(Path("reports/analysis/v112ac_unsupervised_role_challenge_probe_v1.json")),
    )
    assert result.summary["allow_auto_role_replacement_now"] is False
    assert result.summary["allow_auto_training_now"] is False
