from pathlib import Path
import json

from a_share_quant.strategy.v121j_cpo_reduce_side_board_risk_off_external_audit_v1 import (
    V121JCpoReduceSideBoardRiskOffExternalAuditAnalyzer,
)


def test_v121j_reduce_side_board_risk_off_external_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121JCpoReduceSideBoardRiskOffExternalAuditAnalyzer(repo_root=repo_root)
    payload = json.loads(
        (
            repo_root / "reports" / "analysis" / "v121i_cpo_reduce_side_board_risk_off_discovery_v1.json"
        ).read_text(encoding="utf-8")
    )
    result = analyzer.analyze(v121i_payload=payload)
    assert result.summary["best_balanced_accuracy"] >= 0.0
    assert len(result.threshold_audit_rows) > 0
