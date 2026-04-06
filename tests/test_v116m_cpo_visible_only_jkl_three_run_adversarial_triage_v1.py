import json
from pathlib import Path

from a_share_quant.strategy.v116m_cpo_visible_only_jkl_three_run_adversarial_triage_v1 import (
    V116MCpoVisibleOnlyJklThreeRunAdversarialTriageAnalyzer,
)


def test_v116m_visible_only_jkl_triage_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116MCpoVisibleOnlyJklThreeRunAdversarialTriageAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116j_payload=json.loads((repo_root / "reports" / "analysis" / "v116j_cpo_visible_only_broader_shadow_replay_v1.json").read_text(encoding="utf-8")),
        v116k_payload=json.loads((repo_root / "reports" / "analysis" / "v116k_cpo_visible_only_shadow_heat_trim_review_v1.json").read_text(encoding="utf-8")),
        v116l_payload=json.loads((repo_root / "reports" / "analysis" / "v116l_cpo_visible_only_cooled_shadow_retention_v1.json").read_text(encoding="utf-8")),
    )
    assert result.summary["acceptance_posture"] == "freeze_v116m_cpo_visible_only_jkl_three_run_adversarial_triage_v1"
    assert result.summary["corrected_retained_shadow_variant"] == "double_confirm_late_quarter"
    assert result.summary["v116l_retention_valid"] is False
