from pathlib import Path

from a_share_quant.strategy.v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1 import (
    V129YBK0480AerospaceAviationLocalUniverseExpansionAuditAnalyzer,
)


def test_v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V129YBK0480AerospaceAviationLocalUniverseExpansionAuditAnalyzer(repo_root)
    result = analyzer.analyze()

    statuses = {row["symbol"]: row["recommended_local_status"] for row in result.candidate_rows}
    assert result.summary["confirmation_candidates"] == ["600760"]
    assert statuses["002273"] == "quarantine_pending_local_confirmation"
    assert statuses["601989"] == "quarantine_pending_local_confirmation"
    assert statuses["000099"] == "reject_or_mirror_pending"
