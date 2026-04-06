from pathlib import Path
import json

from a_share_quant.strategy.v121n_cpo_reduce_side_out_of_set_false_positive_audit_v1 import (
    V121NCpoReduceSideOutOfSetFalsePositiveAuditAnalyzer,
)


def test_v121n_reduce_side_out_of_set_false_positive_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121NCpoReduceSideOutOfSetFalsePositiveAuditAnalyzer(repo_root=repo_root)
    payload = json.loads((repo_root / "reports" / "analysis" / "v121j_cpo_reduce_side_board_risk_off_external_audit_v1.json").read_text(encoding="utf-8"))
    result = analyzer.analyze(v121j_payload=payload)
    assert result.summary["reduce_pass_rate"] >= 0.0
    assert "add_leakage_rate" in result.summary
