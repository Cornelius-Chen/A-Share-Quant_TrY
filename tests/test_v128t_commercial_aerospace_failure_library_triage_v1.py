from pathlib import Path

from a_share_quant.strategy.v128t_commercial_aerospace_failure_library_triage_v1 import (
    V128TCommercialAerospaceFailureLibraryTriageAnalyzer,
)


def test_v128t_commercial_aerospace_failure_library_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128TCommercialAerospaceFailureLibraryTriageAnalyzer(repo_root).analyze()

    assert int(result.summary["retained_intraday_override_case_count"]) >= 1
    retained_ids = {row["failure_id"] for row in result.retained_rows}
    assert "20260113_601698" in retained_ids
