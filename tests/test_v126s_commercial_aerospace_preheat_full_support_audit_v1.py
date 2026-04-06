from pathlib import Path

from a_share_quant.strategy.v126s_commercial_aerospace_preheat_full_support_audit_v1 import (
    V126SCommercialAerospacePreheatFullSupportAuditAnalyzer,
)


def test_v126s_preheat_full_support_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126SCommercialAerospacePreheatFullSupportAuditAnalyzer(repo_root).analyze()
    assert result.summary["preheat_full_label_count"] >= 0
