from pathlib import Path
import json

from a_share_quant.strategy.v121m_cpo_reduce_side_symbol_holdout_audit_v1 import (
    V121MCpoReduceSideSymbolHoldoutAuditAnalyzer,
)


def test_v121m_reduce_side_symbol_holdout_audit_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121MCpoReduceSideSymbolHoldoutAuditAnalyzer(repo_root=repo_root)
    payload = json.loads((repo_root / "reports" / "analysis" / "v121j_cpo_reduce_side_board_risk_off_external_audit_v1.json").read_text(encoding="utf-8"))
    result = analyzer.analyze(v121j_payload=payload)
    assert result.summary["symbol_holdout_count"] >= 3
    assert result.summary["mean_evaluable_test_balanced_accuracy"] >= 0.0
