from pathlib import Path

from a_share_quant.strategy.v128k_commercial_aerospace_portability_packaging_v1 import (
    V128KCommercialAerospacePortabilityPackagingAnalyzer,
)


def test_v128k_portability_packaging() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V128KCommercialAerospacePortabilityPackagingAnalyzer(repo_root).analyze()

    assert report.summary["current_primary_variant"] == "tail_weakdrift_full"
    assert len(report.portable_rows) >= 4
    assert len(report.local_only_rows) >= 4
