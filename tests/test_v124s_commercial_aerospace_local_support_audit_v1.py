from pathlib import Path

from a_share_quant.strategy.v124s_commercial_aerospace_local_support_audit_v1 import (
    V124SCommercialAerospaceLocalSupportAuditAnalyzer,
)


def test_v124s_supported_count_nonnegative() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V124SCommercialAerospaceLocalSupportAuditAnalyzer(repo_root)
    assert analyzer.universe_path.exists()
