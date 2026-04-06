from pathlib import Path

from a_share_quant.strategy.v126w_commercial_aerospace_preheat_risk_constraint_audit_v1 import (
    V126WCommercialAerospacePreheatRiskConstraintAuditAnalyzer,
)


def test_v126w_preheat_risk_constraint_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126WCommercialAerospacePreheatRiskConstraintAuditAnalyzer(repo_root).analyze()
    assert result.summary["best_variant_final_equity"] > 0
