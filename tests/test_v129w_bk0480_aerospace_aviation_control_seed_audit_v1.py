from pathlib import Path

from a_share_quant.strategy.v129w_bk0480_aerospace_aviation_control_seed_audit_v1 import (
    V129WBK0480AerospaceAviationControlSeedAuditAnalyzer,
)


def test_v129w_bk0480_aerospace_aviation_control_seed_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129WBK0480AerospaceAviationControlSeedAuditAnalyzer(repo_root).analyze()

    assert result.summary["overlap_date_count"] == 16
    assert result.summary["authority_overlap_composite_win_rate"] == 0.625
    assert result.summary["support_role_flip_count"] == 6
