from pathlib import Path

from a_share_quant.strategy.v125d_commercial_aerospace_sentiment_control_boundary_audit_v1 import (
    V125DCommercialAerospaceSentimentControlBoundaryAuditAnalyzer,
)


def test_v125d_produces_boundary_rows_and_tracks_000547() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125DCommercialAerospaceSentimentControlBoundaryAuditAnalyzer(repo_root).analyze()
    assert result.summary["symbol_count"] >= 40
    assert "000547_boundary_semantic" in result.summary
