import json
from pathlib import Path

from a_share_quant.strategy.v123s_cpo_daily_residual_granular_boundary_audit_v1 import (
    V123SCpoDailyResidualGranularBoundaryAuditAnalyzer,
)


def test_v123s_daily_residual_granular_boundary_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    v123m_payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123m_cpo_daily_residual_downside_discovery_v1.json").read_text(
            encoding="utf-8"
        )
    )
    v123r_payload = json.loads(
        (repo_root / "reports" / "analysis" / "v123r_cpo_daily_residual_core_stress_audit_v1.json").read_text(
            encoding="utf-8"
        )
    )
    result = V123SCpoDailyResidualGranularBoundaryAuditAnalyzer(repo_root=repo_root).analyze(
        v123m_payload=v123m_payload,
        v123r_payload=v123r_payload,
    )
    assert result.summary["core_pass_rate"] > result.summary["pre_interval_false_positive_rate"]
