import json
from pathlib import Path

from a_share_quant.strategy.v116p_cpo_visible_only_mno_three_run_adversarial_triage_v1 import (
    V116PCpoVisibleOnlyMnoThreeRunAdversarialTriageAnalyzer,
)


def test_v116p_visible_only_mno_triage_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116PCpoVisibleOnlyMnoThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116m_payload=json.loads((repo_root / "reports" / "analysis" / "v116m_cpo_visible_only_jkl_three_run_adversarial_triage_v1.json").read_text(encoding="utf-8")),
        v116n_payload=json.loads((repo_root / "reports" / "analysis" / "v116n_cpo_corrected_cooled_shadow_retention_v1.json").read_text(encoding="utf-8")),
        v116o_payload=json.loads((repo_root / "reports" / "analysis" / "v116o_cpo_corrected_cooled_shadow_wider_revalidation_v1.json").read_text(encoding="utf-8")),
    )
    assert result.summary["acceptance_posture"] == "freeze_v116p_cpo_visible_only_mno_three_run_adversarial_triage_v1"
    assert result.summary["promotion_allowed"] is False
    assert result.summary["retained_candidate_still_valid"] is True

