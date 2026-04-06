import json
from pathlib import Path

from a_share_quant.strategy.v123r_cpo_daily_residual_core_stress_audit_v1 import (
    V123RCpoDailyResidualCoreStressAuditAnalyzer,
)


def test_v123r_daily_residual_core_stress_focus_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123m_cpo_daily_residual_downside_discovery_v1.json").read_text(
            encoding="utf-8"
        )
    )
    result = V123RCpoDailyResidualCoreStressAuditAnalyzer(repo_root=repo_root).analyze(v123m_payload=payload)
    assert result.summary["core_stress_row_count"] >= 40
    assert result.summary["core_focus_posture"] == "diffuse_inside_interval"
    assert 0.4 <= result.summary["core_above_fringe_rate"] <= 0.6
