from pathlib import Path
import json

from a_share_quant.strategy.v121b_cpo_participation_collapse_close_risk_external_audit_v1 import (
    V121BCpoParticipationCollapseCloseRiskExternalAuditAnalyzer,
)


def test_v121b_close_risk_external_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121BCpoParticipationCollapseCloseRiskExternalAuditAnalyzer(repo_root=repo_root)
    payload = json.loads((repo_root / "reports" / "analysis" / "v121a_cpo_participation_collapse_close_risk_discovery_v1.json").read_text(encoding="utf-8"))
    result = analyzer.analyze(v121a_payload=payload)
    assert result.summary["best_balanced_accuracy"] >= 0.0
    assert len(result.threshold_audit_rows) > 0

