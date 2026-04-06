import json
from pathlib import Path

from a_share_quant.strategy.v116t_cpo_qrs_three_run_adversarial_triage_v1 import (
    V116TCpoQrsThreeRunAdversarialTriageAnalyzer,
)


def test_v116t_qrs_three_run_adversarial_triage_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116TCpoQrsThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116q_payload=json.loads((repo_root / "reports" / "analysis" / "v116q_cpo_expanded_repaired_window_manifest_v1.json").read_text(encoding="utf-8")),
        v116r_payload=json.loads((repo_root / "reports" / "analysis" / "v116r_cpo_corrected_cooled_shadow_expanded_window_validation_v1.json").read_text(encoding="utf-8")),
        v116s_payload=json.loads((repo_root / "reports" / "analysis" / "v116s_cpo_expanded_window_intraday_candidate_coverage_audit_v1.json").read_text(encoding="utf-8")),
    )
    assert result.summary["acceptance_posture"] == "freeze_v116t_cpo_qrs_three_run_adversarial_triage_v1"
    assert result.summary["actual_gap_day_count"] == 3
