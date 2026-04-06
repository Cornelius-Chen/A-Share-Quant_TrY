from pathlib import Path

from a_share_quant.strategy.v129i_commercial_aerospace_late_preheat_entry_mismatch_audit_v1 import (
    V129ICommercialAerospaceLatePreheatEntryMismatchAuditAnalyzer,
)


def test_v129i_commercial_aerospace_late_preheat_entry_mismatch_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129ICommercialAerospaceLatePreheatEntryMismatchAuditAnalyzer(repo_root).analyze()

    assert result.summary["late_preheat_full_order_count"] >= 1
    assert result.summary["late_preheat_full_mismatch_count"] >= 1
